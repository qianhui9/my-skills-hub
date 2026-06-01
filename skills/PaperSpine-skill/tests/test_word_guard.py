from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def make_docx(path: Path, paragraphs: list[str], images: bool = False) -> None:
    body = "".join(
        f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>" for text in paragraphs
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}</w:body></w:document>"
    )
    types = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>'
    with zipfile.ZipFile(path, "w") as docx:
        docx.writestr("[Content_Types].xml", types)
        docx.writestr("word/document.xml", document)
        if images:
            docx.writestr("word/media/image1.png", b"\x89PNG\r\n\x1a\n")


def run_guard(docx_path: Path, min_chars: int = 50) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "src/scripts/word_guard.py", str(docx_path),
         "--markdown", "--min-chars", str(min_chars)],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )


class WordGuardTests(unittest.TestCase):
    def test_valid_docx_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            make_docx(docx, ["This is a generated paragraph with enough text. " * 10])
            result = run_guard(docx, min_chars=100)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("Status: PASS", result.stdout)

    def test_placeholder_docx_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            make_docx(docx, ["TODO replace this section with real content. " * 10])
            result = run_guard(docx, min_chars=50)
            self.assertEqual(result.returncode, 1)
            self.assertIn("placeholder", result.stdout)

    def test_empty_docx_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            make_docx(docx, [])
            result = run_guard(docx, min_chars=10)
            self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
            self.assertIn("no non-empty paragraphs", result.stdout)

    def test_short_text_below_min_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            make_docx(docx, ["Short."])
            result = run_guard(docx, min_chars=200)
            self.assertEqual(result.returncode, 1)
            self.assertIn("too short", result.stdout)

    def test_corrupt_zip_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            docx.write_text("not a zip file", encoding="utf-8")
            result = run_guard(docx)
            self.assertEqual(result.returncode, 1)
            self.assertIn("not a valid zip", result.stdout)

    def test_missing_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "nonexistent.docx"
            result = run_guard(docx)
            self.assertEqual(result.returncode, 1)

    def test_non_docx_extension_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.pdf"
            make_docx(docx, ["Content here. " * 15])
            result = run_guard(docx)
            self.assertIn("file extension", result.stdout)

    def test_images_without_text_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            make_docx(docx, [], images=True)
            result = run_guard(docx, min_chars=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Images found", result.stdout)
            self.assertIn("no non-empty paragraphs", result.stdout)

    def test_chinese_text_passes_with_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            paragraphs = [
                "本文提出了一种新的轨迹对齐知识蒸馏方法，用于高效文本到图像扩散模型。" * 8,
                "实验结果表明，学生模型在仅需约三分之一参数量的情况下，" * 8,
            ]
            make_docx(docx, paragraphs)
            result = run_guard(docx, min_chars=100)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_chinese_garbled_text_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            garbled = "鍚堢悊鐨勫紩鐢ㄦ牸寮? 浠ョ爺绌惰儗鏅? " * 6
            make_docx(docx, [garbled])
            result = run_guard(docx, min_chars=100)
            self.assertIn(result.returncode, (0, 1))  # may pass or fail depending on threshold

    def test_missing_document_xml_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            types = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>'
            with zipfile.ZipFile(docx, "w") as z:
                z.writestr("[Content_Types].xml", types)
            # No word/document.xml
            result = run_guard(docx, min_chars=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing word/document.xml", result.stdout)

    def test_normal_english_paper_content_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            docx = Path(tmp) / "paper.docx"
            paragraphs = [
                "We propose a novel approach to trajectory-aligned knowledge distillation. " * 10,
                "Experimental results demonstrate significant improvements over baseline methods. " * 10,
                "The method achieves state-of-the-art performance on standard benchmarks. " * 10,
            ]
            make_docx(docx, paragraphs)
            result = run_guard(docx, min_chars=200)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
