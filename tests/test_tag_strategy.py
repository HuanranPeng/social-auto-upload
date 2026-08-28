import unittest

from utils.tag_strategy import normalize_tags, refine_tags


class TagStrategyTests(unittest.TestCase):
    def test_normalize_strips_hashes_and_deduplicates_case_insensitively(self):
        self.assertEqual(normalize_tags([" #翻唱 ", "翻唱", "Music", "music"]), ["翻唱", "Music"])

    def test_douyin_balances_tag_tiers(self):
        self.assertEqual(
            refine_tags(
                "douyin",
                exact=["梁博", "曾经是情侣", "额外精准词"],
                category=["翻唱歌曲", "男声翻唱"],
                identity=["硅谷生活"],
                broad=["热门音乐"],
            ),
            ["梁博", "曾经是情侣", "翻唱歌曲", "硅谷生活", "热门音乐"],
        )

    def test_bilibili_prioritizes_two_category_tags_over_broad_tag(self):
        self.assertEqual(
            refine_tags(
                "bilibili",
                exact=["梁博", "曾经是情侣"],
                category=["翻唱", "华语音乐"],
                identity=["男声翻唱"],
                broad=["热门音乐"],
            ),
            ["梁博", "曾经是情侣", "翻唱", "华语音乐", "男声翻唱"],
        )

    def test_custom_limit_fills_from_more_specific_tiers_first(self):
        self.assertEqual(
            refine_tags("tiktok", exact=["ChineseSong", "LiangBo"], category=["VocalCover"], limit=3),
            ["ChineseSong", "LiangBo", "VocalCover"],
        )

    def test_invalid_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            refine_tags("douyin", exact=["test"], limit=0)


if __name__ == "__main__":
    unittest.main()
