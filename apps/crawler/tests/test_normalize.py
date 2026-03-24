import unittest

from anmawon_crawler.normalize import normalize_address, normalize_phone


class NormalizeAddressTest(unittest.TestCase):
    def test_city_alias_is_expanded(self) -> None:
        self.assertEqual(
            normalize_address("서울시 중구 세종대로 1"),
            "서울특별시 중구 세종대로 1",
        )

    def test_whitespace_is_collapsed(self) -> None:
        self.assertEqual(
            normalize_address("  경기   성남시   분당구 "),
            "경기도 성남시 분당구",
        )

    def test_province_alias_is_expanded(self) -> None:
        self.assertEqual(
            normalize_address("충북 청주시 상당구"),
            "충청북도 청주시 상당구",
        )


class NormalizePhoneTest(unittest.TestCase):
    def test_mobile_or_area_code_phone_is_hyphenated(self) -> None:
        self.assertEqual(
            normalize_phone("031 921 2001"),
            "031-921-2001",
        )

    def test_seoul_phone_is_hyphenated(self) -> None:
        self.assertEqual(
            normalize_phone("0212345678"),
            "02-1234-5678",
        )

    def test_existing_short_local_phone_is_preserved(self) -> None:
        self.assertEqual(
            normalize_phone("032-613-782"),
            "032-613-782",
        )


if __name__ == "__main__":
    unittest.main()
