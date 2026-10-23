"""验证用户替换内容和设置后，真实入口与固定测试数据仍各自可用。"""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

from test_template import ROOT, create_workspace, executable


class PersonalizationTests(unittest.TestCase):
    def test_private_inputs_are_explicit_and_cannot_replace_public_examples(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="private-input-", dir=ROOT / "tmp") as directory:
            workspace = create_workspace(Path(directory) / "workspace")
            private = workspace / "resume/private"
            private.mkdir()
            first = private / "content.toml"
            second = private / "content.en.toml"
            first.write_text('[profile]\nname = "PRIVATE_FIRST"\n', encoding="utf-8")
            second.write_text('[profile]\nname = "PRIVATE_SECOND"\n', encoding="utf-8")
            (private / "content with spaces.toml").write_text('[profile]\nname = "PRIVATE_SPACES"\n', encoding="utf-8")
            # 第二个文件更旧，切换内容时仍必须重编译。
            os.utime(second, (1, 1))
            defaults = [(workspace / path).read_bytes() for path in ("resume/content.toml", "resume/content.en.toml")]
            for filename, marker in (("content.toml", "PRIVATE_FIRST"), ("content.en.toml", "PRIVATE_SECOND"),
                                     ("content with spaces.toml", "PRIVATE_SPACES")):
                result = subprocess.run(
                    ["make", "CONTENT=resume/private/" + filename, "TYPST_FLAGS=--ignore-system-fonts"],
                    cwd=workspace, text=True, capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                text = subprocess.check_output([executable("pdftotext"), str(workspace / "output/pdf/personal.pdf"), "-"], text=True)
                self.assertIn(marker, text)
            for target in ("preview", "watch", "info", "en"):
                result = subprocess.run(["make", "--dry-run", target, "CONTENT=resume/private/content.toml"],
                                        cwd=workspace, text=True, capture_output=True, check=True)
                self.assertIn("content=resume/private/content.toml", result.stdout)
            result = subprocess.run(["make", "example", "CONTENT=resume/private/content.toml"],
                                    cwd=workspace, text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("example 仅接受默认公开示例", result.stderr)
            self.assertFalse((workspace / "docs").exists())
            for path, expected in zip(("resume/content.toml", "resume/content.en.toml"), defaults):
                self.assertEqual((workspace / path).read_bytes(), expected)
            result = subprocess.run([executable("typst"), "compile", "--root", ".", "--font-path", "fonts",
                                     "--ignore-system-fonts", "--input", "lang=en", "--input",
                                     "content=resume/private/content.en.toml", "resume.typ", "output/direct.pdf"],
                                    cwd=workspace, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_personalized_content_and_settings_do_not_break_template_tests(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="personalization-", dir=ROOT / "tmp") as directory:
            workspace = create_workspace(Path(directory) / "workspace", include_tests=True)
            # 中文只保留姓名，英文额外保留技能和项目，故意不要求条目数量一致。
            (workspace / "resume/content.toml").write_text(
                '[profile]\nname = "LOCAL_ZH_ONLY"\n', encoding="utf-8",
            )
            (workspace / "resume/content.en.toml").write_text(
                'skills = ["**Editing**: A local fictional entry."]\n'
                '[profile]\nname = "LOCAL_EN_SAMPLE"\n'
                '[[projects]]\ntitle = "Local fictional project"\n'
                'summary = ["Independent English content."]\n', encoding="utf-8",
            )
            settings = (workspace / "resume/settings.toml").read_text().replace('density = 1.00', 'density = 0.96')
            (workspace / "resume/settings.toml").write_text(settings)
            # 原版文件也可使用自定义字体；全小写家族名与 Typst 的匹配方式一致。
            custom_original = settings.replace('"Inter"', '"inter"').replace('"Source Han Serif"', '"source han serif"')
            (workspace / "resume/settings.original.toml").write_text(custom_original)
            environment = os.environ.copy()
            environment.pop("RUN_ORIGINAL_FONT_TESTS", None)
            typst = executable("typst")
            for target in ("pdf", "en", "original", "original-en"):
                result = subprocess.run(
                    ["make", target, "TYPST_FLAGS=--ignore-system-fonts", "TYPST=" + typst],
                    cwd=workspace, env=environment, text=True, capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("warning:", result.stderr)
            for suffix, expected in (("", "LOCAL_ZH_ONLY"), ("-en", "LOCAL_EN_SAMPLE"),
                                     ("-original", "LOCAL_ZH_ONLY"), ("-original-en", "LOCAL_EN_SAMPLE")):
                result = subprocess.run(
                    [executable("pdftotext"), "-layout", str(workspace / ("output/pdf/resume" + suffix + ".pdf")), "-"],
                    cwd=workspace, text=True, capture_output=True, check=True,
                )
                self.assertIn(expected, result.stdout)
                self.assertNotIn("排版测试", result.stdout)
            result = subprocess.run(
                [sys.executable, "tests/test_template.py"], cwd=workspace, env=environment,
                text=True, capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            print("Personalized content, independent language sections, custom fonts and fixture tests passed.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
