import unittest

import httpx
from bs4 import BeautifulSoup

from anmawon_crawler.crawler import (
    build_list_url,
    discover_area_codes,
    discover_page_count,
    extract_address_from_page,
    extract_detail_urls,
    extract_name_from_page,
    extract_phone_from_page,
    fetch_html,
    parse_key_value_pairs,
)


def soup_from_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


class BuildListUrlTest(unittest.TestCase):
    def test_uses_custom_base_url(self) -> None:
        self.assertEqual(
            build_list_url(base_url="https://example.com"),
            "https://example.com/FindShop/List",
        )

    def test_includes_area_and_page_params(self) -> None:
        self.assertEqual(
            build_list_url(
                area_code="031",
                page=3,
                base_url="https://example.com/",
            ),
            "https://example.com/FindShop/List?SearchArea=031&page=3",
        )


class ListParsingTest(unittest.TestCase):
    def test_discovers_area_codes_from_links_and_options(self) -> None:
        soup = soup_from_html(
            """
            <html>
              <body>
                <a href="/FindShop/List?SearchArea=031">031</a>
                <a href="/FindShop/List?SearchArea=02&page=2">02</a>
                <a onclick="location.href='/FindShop/List?SearchArea=064'">제주</a>
                <select>
                  <option value="051">부산</option>
                  <option value="/FindShop/List?SearchArea=031">경기</option>
                  <option value="">전지역</option>
                  <option value="1">=선택=</option>
                </select>
              </body>
            </html>
            """
        )

        self.assertEqual(discover_area_codes(soup), ["02", "031", "051", "064"])

    def test_discovers_highest_page_number(self) -> None:
        soup = soup_from_html(
            """
            <html>
              <body>
                <a href="/FindShop/List?page=1">1</a>
                <a href="/FindShop/List?page=4">4</a>
                <a href="/FindShop/List?page=12">12</a>
                <button onclick="goPage(9)">9</button>
              </body>
            </html>
            """
        )

        self.assertEqual(discover_page_count(soup), 12)

    def test_ignores_detail_page_params_when_counting_pages(self) -> None:
        soup = soup_from_html(
            """
            <html>
              <body>
                <a href="/FindShop/Detail?page=77&shopId=031-0193">상세</a>
                <a href="/FindShop/List?page=3">3</a>
              </body>
            </html>
            """
        )

        self.assertEqual(discover_page_count(soup), 3)

    def test_extracts_unique_absolute_detail_urls(self) -> None:
        soup = soup_from_html(
            """
            <html>
              <body>
                <a href="/FindShop/Detail?page=1&shopId=031-0193">상세</a>
                <a href="https://example.com/FindShop/Detail?page=1&shopId=031-0193">중복</a>
                <a href="/FindShop/Detail?page=2&shopId=02-0001">상세</a>
              </body>
            </html>
            """
        )

        self.assertEqual(
            extract_detail_urls(soup, base_url="https://example.com"),
            [
                "https://example.com/FindShop/Detail?page=1&shopId=031-0193",
                "https://example.com/FindShop/Detail?page=2&shopId=02-0001",
            ],
        )


class DetailParsingTest(unittest.TestCase):
    def test_extracts_name_address_and_phone_from_table(self) -> None:
        soup = soup_from_html(
            """
            <html>
              <body>
                <table>
                  <tr><th>상호명</th><td>예시 안마원</td></tr>
                  <tr><th>주소</th><td>서울시 중구 세종대로 1</td></tr>
                  <tr><th>전화번호</th><td>02-1234-5678</td></tr>
                </table>
              </body>
            </html>
            """
        )

        pairs = parse_key_value_pairs(soup)

        self.assertEqual(extract_name_from_page(soup, pairs), "예시 안마원")
        self.assertEqual(extract_address_from_page(soup, pairs), "서울시 중구 세종대로 1")
        self.assertEqual(extract_phone_from_page(soup, pairs), "02-1234-5678")

    def test_falls_back_to_heading_and_text_search(self) -> None:
        soup = soup_from_html(
            """
            <html>
              <head><title>대표 안마원 | 국가안마원</title></head>
              <body>
                <h1>대표 안마원</h1>
                <p>주소: 경기 성남시 분당구 판교로 123</p>
                <p>문의 031-123-4567</p>
              </body>
            </html>
            """
        )

        pairs = parse_key_value_pairs(soup)

        self.assertEqual(extract_name_from_page(soup, pairs), "대표 안마원")
        self.assertEqual(extract_address_from_page(soup, pairs), "경기 성남시 분당구 판교로 123")
        self.assertEqual(extract_phone_from_page(soup, pairs), "031-123-4567")


class FetchHtmlTest(unittest.TestCase):
    def test_wraps_network_errors_with_context(self) -> None:
        class FailingClient:
            def get(self, url: str):
                raise httpx.ConnectError(
                    "Connection reset by peer",
                    request=httpx.Request("GET", url),
                )

        with self.assertRaises(RuntimeError) as context:
            fetch_html(FailingClient(), "https://www.anmawon.com/FindShop/List")

        self.assertIn("https://www.anmawon.com/FindShop/List", str(context.exception))
        self.assertIn("network error", str(context.exception))


if __name__ == "__main__":
    unittest.main()
