import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

import sau_cli
from uploader.tk_uploader.main_chrome import TiktokVideo


class TiktokUploaderSafetyTests(unittest.TestCase):
    def test_publish_requires_explicit_mode_before_browser_launch(self):
        app = TiktokVideo("title", "video.mp4", [], 0, "account.json")
        playwright = MagicMock()

        with self.assertRaisesRegex(ValueError, "implicit TikTok publishing"):
            asyncio.run(app.upload(playwright))

        playwright.chromium.launch.assert_not_called()

    def test_dry_run_is_explicitly_recorded(self):
        app = TiktokVideo("title", "video.mp4", [], 0, "account.json", dry_run=True)
        self.assertTrue(app.dry_run)
        self.assertFalse(app.confirm_publish)

    def test_cli_accepts_explicit_dry_run_and_thumbnail(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            account = Path(tmp_dir) / "account.json"
            video = Path(tmp_dir) / "video.mp4"
            cover = Path(tmp_dir) / "cover.png"
            for path in (account, video, cover):
                path.write_bytes(b"test")
            args = sau_cli.build_parser().parse_args([
                "tiktok", "upload-video", "--account-file", str(account),
                "--file", str(video), "--title", "Caption", "--tags", "One,#Two",
                "--thumbnail", str(cover), "--dry-run",
            ])
        self.assertTrue(args.dry_run)
        self.assertEqual(args.thumbnail, cover)

    def test_cli_rejects_implicit_publish(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            account = Path(tmp_dir) / "account.json"
            video = Path(tmp_dir) / "video.mp4"
            account.write_bytes(b"test")
            video.write_bytes(b"test")
            with self.assertRaises(SystemExit):
                sau_cli.build_parser().parse_args([
                    "tiktok", "upload-video", "--account-file", str(account),
                    "--file", str(video), "--title", "Caption",
                ])


if __name__ == "__main__":
    unittest.main()
