import json
import unittest

import httpx

from anmawon_crawler.probe import (
    build_probe_targets,
    format_probe_report,
    probe_url,
)


class BuildProbeTargetsTest(unittest.TestCase):
    def test_adds_http_fallback_for_https_base_url(self) -> None:
        self.assertEqual(
            build_probe_targets("https://www.anmawon.com"),
            [
                ("configured-list", "https://www.anmawon.com/FindShop/List"),
                ("http-fallback-list", "http://www.anmawon.com/FindShop/List"),
            ],
        )

    def test_keeps_single_target_for_http_base_url(self) -> None:
        self.assertEqual(
            build_probe_targets("http://www.anmawon.com"),
            [("configured-list", "http://www.anmawon.com/FindShop/List")],
        )


class ProbeUrlTest(unittest.TestCase):
    def test_reports_http_status(self) -> None:
        client = httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, request=request)
            )
        )

        result = probe_url(client, "configured-list", "https://example.com/FindShop/List")

        self.assertTrue(result.ok)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.detail, "HTTP 200")

    def test_reports_network_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("Connection reset by peer", request=request)

        client = httpx.Client(transport=httpx.MockTransport(handler))

        result = probe_url(client, "configured-list", "https://example.com/FindShop/List")

        self.assertFalse(result.ok)
        self.assertIn("ConnectError", result.detail)


class FormatProbeReportTest(unittest.TestCase):
    def test_formats_json_payload(self) -> None:
        payload = format_probe_report(
            "https://www.anmawon.com/",
            [],
        )

        parsed = json.loads(payload)
        self.assertEqual(parsed["baseUrl"], "https://www.anmawon.com")
        self.assertEqual(parsed["results"], [])


if __name__ == "__main__":
    unittest.main()
