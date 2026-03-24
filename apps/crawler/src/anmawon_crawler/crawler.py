from __future__ import annotations

import re
import time
from dataclasses import replace
from typing import Dict, Iterable, List, Optional, Sequence, Set
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from .models import ShopRecord
from .storage import now_iso


DEFAULT_BASE_URL = "https://www.anmawon.com"
LIST_PATH = "/FindShop/List"
DETAIL_PATH = "/FindShop/Detail"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)

NAME_KEYS = ("상호명", "업소명", "상호", "안마원명", "기관명")
ADDRESS_KEYS = ("주소", "소재지", "도로명주소")
PHONE_KEYS = ("전화번호", "전화", "연락처", "대표번호")

PHONE_PATTERN = re.compile(r"0\d{1,2}-\d{3,4}-\d{4}")
ADDRESS_HINT_PATTERN = re.compile(
    r"(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)"
)


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def build_list_url(
    area_code: Optional[str] = None,
    page: int = 1,
    *,
    base_url: str = DEFAULT_BASE_URL,
) -> str:
    params = {}
    normalized_base_url = normalize_base_url(base_url)

    if area_code:
        params["SearchArea"] = area_code

    if page > 1:
        params["page"] = str(page)

    if not params:
        return urljoin(normalized_base_url, LIST_PATH)

    return f"{urljoin(normalized_base_url, LIST_PATH)}?{urlencode(params)}"


def extract_query_values(text: str, key: str) -> List[str]:
    values: Set[str] = set()

    if "?" in text:
        query = parse_qs(urlparse(text).query)
        values.update(query.get(key, []))

    pattern = re.compile(rf"{re.escape(key)}=([0-9A-Za-z-]+)")
    values.update(match.group(1) for match in pattern.finditer(text))
    return sorted(values)


def discover_area_codes(soup: BeautifulSoup) -> List[str]:
    area_codes: Set[str] = set()

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        area_codes.update(extract_query_values(href, "SearchArea"))

    for option in soup.select("option[value]"):
        value = option.get("value", "")
        area_codes.update(extract_query_values(value, "SearchArea"))
        if value.isdigit():
            area_codes.add(value)

    return sorted(code for code in area_codes if code)


def discover_page_count(soup: BeautifulSoup) -> int:
    pages: Set[int] = {1}

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        for value in extract_query_values(href, "page"):
            if value.isdigit():
                pages.add(int(value))

    return max(pages)


def extract_detail_urls(
    soup: BeautifulSoup,
    *,
    base_url: str = DEFAULT_BASE_URL,
) -> List[str]:
    detail_urls: List[str] = []
    seen: Set[str] = set()
    normalized_base_url = normalize_base_url(base_url)

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")

        if DETAIL_PATH not in href or "shopId=" not in href:
            continue

        absolute_url = urljoin(normalized_base_url, href)

        if absolute_url in seen:
            continue

        seen.add(absolute_url)
        detail_urls.append(absolute_url)

    return detail_urls


def extract_shop_id(detail_url: str) -> str:
    return parse_qs(urlparse(detail_url).query).get("shopId", [""])[0]


def extract_area_code(detail_url: str) -> str:
    shop_id = extract_shop_id(detail_url)

    if "-" in shop_id:
        return shop_id.split("-", 1)[0]

    return ""


def flatten_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_key_value_pairs(soup: BeautifulSoup) -> Dict[str, str]:
    pairs: Dict[str, str] = {}

    for row in soup.select("tr"):
        header = row.find("th")
        cell = row.find("td")
        if not header or not cell:
            continue

        key = flatten_text(header.get_text(" ", strip=True)).rstrip(":")
        value = flatten_text(cell.get_text(" ", strip=True))
        if key and value:
            pairs[key] = value

    for block in soup.select("dl"):
        terms = block.find_all("dt")
        descriptions = block.find_all("dd")
        for term, description in zip(terms, descriptions):
            key = flatten_text(term.get_text(" ", strip=True)).rstrip(":")
            value = flatten_text(description.get_text(" ", strip=True))
            if key and value and key not in pairs:
                pairs[key] = value

    for item in soup.select("li, p"):
        text = flatten_text(item.get_text(" ", strip=True))
        if ":" not in text:
            continue
        key, value = [part.strip() for part in text.split(":", 1)]
        if key and value and len(key) <= 12 and key not in pairs:
            pairs[key] = value

    return pairs


def pick_first(pairs: Dict[str, str], keys: Sequence[str]) -> str:
    for key in keys:
        if pairs.get(key):
            return pairs[key]
    return ""


def extract_name_from_page(soup: BeautifulSoup, pairs: Dict[str, str]) -> str:
    explicit = pick_first(pairs, NAME_KEYS)
    if explicit:
        return explicit

    heading = soup.find(["h1", "h2", "strong"])
    if heading:
        return flatten_text(heading.get_text(" ", strip=True))

    title = soup.title.string if soup.title and soup.title.string else ""
    return flatten_text(title.replace("|", " ").replace("-", " "))


def extract_address_from_page(soup: BeautifulSoup, pairs: Dict[str, str]) -> str:
    explicit = pick_first(pairs, ADDRESS_KEYS)
    if explicit:
        return explicit

    for text in soup.stripped_strings:
        candidate = flatten_text(text)
        if ADDRESS_HINT_PATTERN.search(candidate) and len(candidate) >= 8:
            return candidate

    return ""


def extract_phone_from_page(soup: BeautifulSoup, pairs: Dict[str, str]) -> str:
    explicit = pick_first(pairs, PHONE_KEYS)
    if explicit:
        match = PHONE_PATTERN.search(explicit)
        return match.group(0) if match else explicit

    match = PHONE_PATTERN.search(soup.get_text(" ", strip=True))
    return match.group(0) if match else ""


def fetch_html(client: httpx.Client, url: str) -> BeautifulSoup:
    try:
        response = client.get(url)
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        raise RuntimeError(f"Failed to fetch {url} (status {status_code}).") from error
    except httpx.HTTPError as error:
        raise RuntimeError(
            f"Failed to fetch {url} due to a network error: {error}. "
            "If the live source resets the connection in your environment, "
            "verify the URL with ANMAWON_BASE_URL or retry from a network that can reach the source."
        ) from error

    return BeautifulSoup(response.text, "html.parser")


def parse_detail_page(
    client: httpx.Client,
    detail_url: str,
    source_list_page: Optional[int],
) -> ShopRecord:
    soup = fetch_html(client, detail_url)
    pairs = parse_key_value_pairs(soup)

    return ShopRecord(
        shop_id=extract_shop_id(detail_url),
        name=extract_name_from_page(soup, pairs),
        address_raw=extract_address_from_page(soup, pairs),
        area_code=extract_area_code(detail_url),
        phone=extract_phone_from_page(soup, pairs),
        source_list_page=source_list_page,
        detail_url=detail_url,
        source_fetched_at=now_iso(),
    )


def crawl_directory(
    *,
    area_codes: Optional[Iterable[str]],
    base_url: str = DEFAULT_BASE_URL,
    request_delay: float,
    timeout: float,
    user_agent: str = DEFAULT_USER_AGENT,
    max_pages_per_area: Optional[int] = None,
) -> List[ShopRecord]:
    headers = {
        "User-Agent": user_agent or DEFAULT_USER_AGENT
    }

    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        root_soup = fetch_html(client, build_list_url(base_url=base_url))
        discovered_area_codes = discover_area_codes(root_soup)
        active_area_codes = list(area_codes) if area_codes else discovered_area_codes or [""]
        discovered_links: Dict[str, ShopRecord] = {}

        for area_code in active_area_codes:
            first_page_url = build_list_url(
                area_code=area_code or None,
                page=1,
                base_url=base_url,
            )
            list_soup = fetch_html(client, first_page_url)
            page_count = discover_page_count(list_soup)

            if max_pages_per_area is not None:
                page_count = min(page_count, max_pages_per_area)

            for page in range(1, page_count + 1):
                page_url = build_list_url(
                    area_code=area_code or None,
                    page=page,
                    base_url=base_url,
                )
                soup = list_soup if page == 1 else fetch_html(client, page_url)

                for detail_url in extract_detail_urls(soup, base_url=base_url):
                    shop_id = extract_shop_id(detail_url)
                    if not shop_id:
                        continue

                    discovered_links[shop_id] = ShopRecord(
                        shop_id=shop_id,
                        area_code=area_code,
                        detail_url=detail_url,
                        source_list_page=page,
                    )

                time.sleep(request_delay)

        records: List[ShopRecord] = []

        for seed in discovered_links.values():
            detailed_record = parse_detail_page(
                client,
                seed.detail_url,
                seed.source_list_page,
            )
            if seed.area_code and not detailed_record.area_code:
                detailed_record = replace(detailed_record, area_code=seed.area_code)

            records.append(detailed_record)
            time.sleep(request_delay)

        return sorted(records, key=lambda item: item.shop_id)
