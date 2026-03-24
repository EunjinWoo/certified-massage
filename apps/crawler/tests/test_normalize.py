import unittest

from anmawon_crawler.normalize import normalize_address


class NormalizeAddressTest(unittest.TestCase):
    def test_city_alias_is_expanded(self) -> None:
        self.assertEqual(
            normalize_address("서울시 중구 세종대로 1"),
            "서울특별시 중구 세종대로 1",
        )

    def test_whitespace_is_collapsed(self) -> None:
        self.assertEqual(
            normalize_address("  경기   성남시   분당구 "),
            "경기 성남시 분당구",
        )


if __name__ == "__main__":
    unittest.main()
