import json
import tempfile
import unittest
from pathlib import Path

from jsonschema.exceptions import ValidationError

from anmawon_crawler.validate import validate_dataset_file, validate_dataset_payload


VALID_PAYLOAD = {
    "generatedAt": "2026-03-24T00:00:00+09:00",
    "count": 1,
    "shops": [
        {
            "shopId": "031-0193",
            "name": "예시 안마원",
            "addressRaw": "경기도 성남시 분당구 판교로 1",
            "addressNormalized": "경기도 성남시 분당구 판교로 1",
            "phone": "031-123-4567",
            "areaCode": "031",
            "sourceListPage": 1,
            "detailUrl": "http://www.anmawon.com/FindShop/Detail?shopId=031-0193&page=1&SearchArea=031",
            "lat": 37.4,
            "lng": 127.1,
            "geocodeStatus": "success",
            "sourceFetchedAt": "2026-03-24T00:00:00+09:00",
        }
    ],
}


class ValidateDatasetPayloadTest(unittest.TestCase):
    def test_accepts_valid_payload(self) -> None:
        validate_dataset_payload(VALID_PAYLOAD)

    def test_rejects_missing_required_field(self) -> None:
        invalid_shop = dict(VALID_PAYLOAD["shops"][0])
        invalid_shop.pop("detailUrl")
        invalid_payload = {**VALID_PAYLOAD, "shops": [invalid_shop]}

        with self.assertRaises(ValidationError) as context:
            validate_dataset_payload(invalid_payload)

        self.assertIn("detailUrl", str(context.exception))

    def test_rejects_count_type_mismatch(self) -> None:
        invalid_payload = {
            **VALID_PAYLOAD,
            "count": "1",
        }

        with self.assertRaises(ValidationError) as context:
            validate_dataset_payload(invalid_payload)

        self.assertIn("count", str(context.exception))


class ValidateDatasetFileTest(unittest.TestCase):
    def test_validates_dataset_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "shops.geo.json"
            path.write_text(json.dumps(VALID_PAYLOAD), encoding="utf-8")
            validate_dataset_file(path)

    def test_current_repo_dataset_is_valid(self) -> None:
        validate_dataset_file()


if __name__ == "__main__":
    unittest.main()
