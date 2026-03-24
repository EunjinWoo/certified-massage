import unittest

import httpx

from anmawon_crawler.geocode import apply_geocoding, geocode_address
from anmawon_crawler.models import ShopRecord


class GeocodeAddressTest(unittest.TestCase):
    def test_returns_coordinates_for_successful_response(self) -> None:
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={"documents": [{"x": "127.1", "y": "37.5"}]},
                    request=request,
                )
            )
        )

        lat, lng, status, detail = geocode_address(client, "test-key", "서울특별시")

        self.assertEqual((lat, lng, status, detail), (37.5, 127.1, "success", None))

    def test_returns_not_found_for_empty_documents(self) -> None:
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"documents": []}, request=request)
            )
        )

        lat, lng, status, detail = geocode_address(client, "test-key", "없는 주소")

        self.assertEqual((lat, lng, status, detail), (None, None, "failed", "not_found"))


class ApplyGeocodingTest(unittest.TestCase):
    def test_uses_cache_and_records_summary(self) -> None:
        records = [
            ShopRecord(
                shop_id="031-0011",
                address_normalized="경기도 고양시",
                detail_url="http://example.com/detail/1",
            )
        ]
        cache = {
            "경기도 고양시": {
                "lat": 37.1,
                "lng": 127.1,
                "status": "success",
            }
        }
        client = httpx.Client(transport=httpx.MockTransport(lambda request: None))

        results, _, failures, summary = apply_geocoding(
            records,
            api_key="test-key",
            timeout=5,
            cache=cache,
            client=client,
        )

        self.assertEqual(results[0].geocode_status, "success")
        self.assertEqual(results[0].lat, 37.1)
        self.assertEqual(failures, [])
        self.assertEqual(summary["cacheHits"], 1)
        self.assertEqual(summary["success"], 1)

    def test_records_api_failure_details(self) -> None:
        records = [
            ShopRecord(
                shop_id="031-0040",
                address_normalized="경기도 부천시",
                detail_url="http://example.com/detail/2",
            )
        ]
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"documents": []}, request=request)
            )
        )

        _, cache, failures, summary = apply_geocoding(
            records,
            api_key="test-key",
            timeout=5,
            cache={},
            client=client,
        )

        self.assertEqual(cache["경기도 부천시"]["reason"], "not_found")
        self.assertEqual(failures[0]["reason"], "not_found")
        self.assertEqual(failures[0]["source"], "api")
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["failureReasons"]["not_found"], 1)

    def test_records_missing_address_as_skipped(self) -> None:
        records = [ShopRecord(shop_id="031-0099", detail_url="http://example.com/detail/3")]
        client = httpx.Client(transport=httpx.MockTransport(lambda request: None))

        results, _, failures, summary = apply_geocoding(
            records,
            api_key="test-key",
            timeout=5,
            cache={},
            client=client,
        )

        self.assertEqual(results[0].geocode_status, "skipped")
        self.assertEqual(failures[0]["reason"], "missing_address")
        self.assertEqual(summary["skipped"], 1)


if __name__ == "__main__":
    unittest.main()
