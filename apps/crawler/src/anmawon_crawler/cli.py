from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .crawler import crawl_directory
from .geocode import apply_geocoding
from .normalize import clean_records
from .probe import format_probe_report, run_source_probe
from .settings import load_settings
from .storage import (
    CLEAN_DATA_PATH,
    FINAL_DATA_PATH,
    GEOCODE_CACHE_PATH,
    GEOCODE_FAILURE_PATH,
    GEOCODED_DATA_PATH,
    RAW_DATA_PATH,
    read_dataset,
    read_json,
    write_dataset,
    write_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anmawon-crawler",
        description="Crawler pipeline for the certified massage map project",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    crawl_parser = subparsers.add_parser("crawl", help="Fetch list/detail pages")
    crawl_parser.add_argument(
        "--area-code",
        action="append",
        help="Optional area code filter. Repeat to fetch multiple codes.",
    )
    crawl_parser.add_argument(
        "--max-pages-per-area",
        type=int,
        default=None,
        help="Limit pagination per area during development.",
    )

    subparsers.add_parser("clean", help="Normalize addresses and text fields")
    subparsers.add_parser("geocode", help="Resolve coordinates with Kakao Local API")
    subparsers.add_parser(
        "probe-source",
        help="Check live source reachability before running crawl",
    )
    subparsers.add_parser(
        "build-dataset",
        help="Promote the latest processed file to the final dataset",
    )
    return parser


def command_crawl(area_codes, max_pages_per_area: int | None) -> None:
    settings = load_settings()
    records = crawl_directory(
        area_codes=area_codes,
        base_url=settings.anmawon_base_url,
        request_delay=settings.request_delay,
        timeout=settings.timeout,
        user_agent=settings.anmawon_user_agent,
        max_pages_per_area=max_pages_per_area,
    )
    write_dataset(RAW_DATA_PATH, records)
    print(f"Wrote {len(records)} records to {RAW_DATA_PATH}")


def command_clean() -> None:
    records = read_dataset(RAW_DATA_PATH)
    cleaned = clean_records(records)
    write_dataset(CLEAN_DATA_PATH, cleaned)
    print(f"Wrote {len(cleaned)} records to {CLEAN_DATA_PATH}")


def command_geocode() -> None:
    settings = load_settings()
    records = read_dataset(CLEAN_DATA_PATH)
    cache = read_json(GEOCODE_CACHE_PATH, default={})
    geocoded, cache, failures, summary = apply_geocoding(
        records,
        api_key=settings.kakao_rest_api_key,
        timeout=settings.timeout,
        cache=cache,
    )
    write_dataset(GEOCODED_DATA_PATH, geocoded)
    write_json(GEOCODE_CACHE_PATH, cache)
    write_json(
        GEOCODE_FAILURE_PATH,
        {
            "count": len(failures),
            "summary": summary,
            "failures": failures,
        },
    )
    print(f"Wrote {len(geocoded)} records to {GEOCODED_DATA_PATH}")


def command_probe_source() -> None:
    settings = load_settings()
    results = run_source_probe(
        base_url=settings.anmawon_base_url,
        timeout=settings.timeout,
        user_agent=settings.anmawon_user_agent,
    )
    print(format_probe_report(settings.anmawon_base_url, results))


def command_build_dataset() -> None:
    source_path = GEOCODED_DATA_PATH if GEOCODED_DATA_PATH.exists() else CLEAN_DATA_PATH
    records = read_dataset(source_path)
    write_dataset(FINAL_DATA_PATH, records)
    print(f"Promoted {len(records)} records from {source_path} to {FINAL_DATA_PATH}")


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "crawl":
        command_crawl(args.area_code, args.max_pages_per_area)
        return

    if args.command == "clean":
        command_clean()
        return

    if args.command == "geocode":
        command_geocode()
        return

    if args.command == "probe-source":
        command_probe_source()
        return

    if args.command == "build-dataset":
        command_build_dataset()
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
