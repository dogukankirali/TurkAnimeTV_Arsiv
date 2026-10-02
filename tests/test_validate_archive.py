import json
import tempfile
import unittest
from pathlib import Path

from validate_archive import validate_archive


def write_fixture(root: Path) -> None:
    (root / "b").mkdir(parents=True)
    episode = [{"no": 1, "ad": "Episode 1", "slug": "sample-1", "links": [
        {"player": "MAIL", "fansub": "Group", "tip": "url", "url": "https://example.test/video"}
    ]}]
    (root / "b" / "sample.js").write_text(
        'window.__TKA__=window.__TKA__||{};window.__TKA__["sample"]='
        + json.dumps(episode) + ";\n",
        encoding="utf-8",
    )
    index = [["sample", "Sample", 1, 1, 0, ["MAIL"]]]
    (root / "search.html").write_text(
        "<!doctype html><html><head><title>Test</title><style>body{}</style></head><body>"
        "<script>window.INDEX = /*INDEX_START*/"
        + json.dumps(index)
        + "/*INDEX_END*/;</script></body></html>",
        encoding="utf-8",
    )
    (root / "index.html").write_text(
        '<meta http-equiv="refresh" content="0;url=search.html">',
        encoding="utf-8",
    )
    (root / "kaldirilan.js").write_text("window.KALDIRILAN = [];\n", encoding="utf-8")
    (root / "eklenen.js").write_text("window.EKLENEN = [];\n", encoding="utf-8")


class ValidateArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        write_fixture(self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_accepts_a_consistent_archive(self) -> None:
        self.assertEqual(validate_archive(self.root), [])

    def test_reports_malformed_anime_jsonp(self) -> None:
        (self.root / "b" / "sample.js").write_text("window.__TKA__[", encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("b/sample.js" in error for error in errors), errors)

    def test_reports_index_counter_mismatch(self) -> None:
        path = self.root / "search.html"
        path.write_text(path.read_text(encoding="utf-8").replace('"Sample", 1, 1, 0', '"Sample", 2, 1, 0'), encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("sample" in error and "episode" in error.lower() for error in errors), errors)

    def test_requires_index_markers_inside_window_index_assignment(self) -> None:
        path = self.root / "search.html"
        path.write_text(path.read_text(encoding="utf-8").replace("window.INDEX =", "window.NOT_INDEX ="), encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("window.INDEX assignment" in error for error in errors), errors)

    def test_rejects_a_second_window_index_assignment(self) -> None:
        path = self.root / "search.html"
        path.write_text(path.read_text(encoding="utf-8").replace("</body>", "<script>window.INDEX = [];</script></body>"), encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("exactly one window.INDEX assignment" in error for error in errors), errors)

    def test_reports_anime_missing_from_index(self) -> None:
        path = self.root / "search.html"
        path.write_text(path.read_text(encoding="utf-8").replace('["sample", "Sample", 1, 1, 0, ["MAIL"]]', ''), encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("sample" in error and "INDEX" in error for error in errors), errors)

    def test_reports_invalid_override_data(self) -> None:
        (self.root / "kaldirilan.js").write_text("window.KALDIRILAN = [1];", encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("kaldirilan.js" in error for error in errors), errors)

    def test_rejects_executable_code_after_override_data(self) -> None:
        (self.root / "kaldirilan.js").write_text(
            'window.KALDIRILAN = []; window.KALDIRILAN.push("https://example.test/x");',
            encoding="utf-8",
        )
        errors = validate_archive(self.root)
        self.assertTrue(any("unexpected code" in error for error in errors), errors)

    def test_reports_unclosed_script_element(self) -> None:
        path = self.root / "search.html"
        path.write_text(path.read_text(encoding="utf-8").replace("</script>", ""), encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("script" in error.lower() for error in errors), errors)

    def test_reports_inline_javascript_syntax_error(self) -> None:
        path = self.root / "search.html"
        path.write_text(path.read_text(encoding="utf-8").replace("window.INDEX =", "window.INDEX = )"), encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("inline" in error.lower() and "syntax" in error.lower() for error in errors), errors)

    def test_reports_unclosed_style_element(self) -> None:
        path = self.root / "search.html"
        path.write_text(path.read_text(encoding="utf-8").replace("</style>", ""), encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("style" in error.lower() for error in errors), errors)

    def test_reports_missing_index_redirect(self) -> None:
        (self.root / "index.html").write_text('<meta http-equiv="refresh" content="0;url=other.html">', encoding="utf-8")
        errors = validate_archive(self.root)
        self.assertTrue(any("index.html" in error and "search.html" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
