import unittest

from scripts.research.cloudflare_r2_diagnostics import validate_config


BASE = {
    "CF_R2_ACCOUNT_ID": "0123456789abcdef0123456789abcdef",
    "CF_R2_ACCESS_KEY_ID": "test-access-key",
    "CF_R2_SECRET_ACCESS_KEY": "test-secret",
}


class CloudflareR2ConfigTests(unittest.TestCase):
    def test_defaults_are_bucket_and_prefix_scoped(self):
        cfg = validate_config(BASE)
        self.assertEqual(cfg["bucket"], "sp2l-forward-evidence")
        self.assertEqual(cfg["prefix"], "forward-test/")
        self.assertTrue(cfg["endpoint"].startswith("https://"))

    def test_normalizes_prefix_trailing_slash(self):
        cfg = validate_config({**BASE, "CF_R2_PREFIX": "forward-test"})
        self.assertEqual(cfg["prefix"], "forward-test/")

    def test_rejects_absolute_prefix(self):
        with self.assertRaisesRegex(ValueError, "relative object prefix"):
            validate_config({**BASE, "CF_R2_PREFIX": "/forward-test/"})

    def test_rejects_parent_traversal_segment(self):
        with self.assertRaisesRegex(ValueError, "relative object prefix"):
            validate_config({**BASE, "CF_R2_PREFIX": "forward-test/../other/"})

    def test_rejects_missing_secret(self):
        env = dict(BASE)
        env.pop("CF_R2_SECRET_ACCESS_KEY")
        with self.assertRaisesRegex(ValueError, "CF_R2_SECRET_ACCESS_KEY"):
            validate_config(env)

    def test_rejects_invalid_account_id(self):
        with self.assertRaisesRegex(ValueError, "unexpected format"):
            validate_config({**BASE, "CF_R2_ACCOUNT_ID": "bad/id"})


if __name__ == "__main__":
    unittest.main()
