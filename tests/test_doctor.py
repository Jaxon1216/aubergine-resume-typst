"""环境检查必须区分导出依赖、可选工具和真正缺失的字体。"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_template import ROOT, create_workspace


class DoctorTests(unittest.TestCase):
    def invoke(self, *args, root=ROOT, **environment):
        return subprocess.run([sys.executable, "scripts/doctor.py", *args], cwd=root,
                              env={**os.environ, **environment}, text=True, capture_output=True)

    def test_optional_preview_tool_does_not_block_export(self):
        result = self.invoke("--ignore-system-fonts", TINYMIST="not-installed-fixture", MAKE="not-installed-fixture")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("可选，未安装 tinymist", result.stdout)
        self.assertIn("可选，未安装 make", result.stdout)

    def test_missing_required_tool_has_actionable_error(self):
        for args, env, name in (((), {"TYPST": "not-installed-fixture"}, "typst"),
                                (("--preview",), {"TINYMIST": "not-installed-fixture"}, "tinymist"),
                                (("--tests",), {"PDFINFO": "not-installed-fixture"}, "pdfinfo")):
            with self.subTest(name=name):
                result = self.invoke(*args, **env)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("未找到 " + name, result.stderr)

    def test_missing_font_is_reported_from_selected_settings(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            workspace = create_workspace(Path(directory) / "workspace")
            settings = workspace / "resume/settings.toml"
            settings.write_text(settings.read_text().replace('"Inter"', '"Missing Doctor Fixture Font"'))
            result = self.invoke("--ignore-system-fonts", root=workspace)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("当前设置缺少字体：Missing Doctor Fixture Font", result.stderr)

    def test_modified_bundled_font_fails_checksum(self):
        (ROOT / "tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            workspace = create_workspace(Path(directory) / "workspace")
            # 附加字节保持字体可读，但不应绕过文件完整性校验。
            with (workspace / "fonts/Inter/InterVariable.ttf").open("ab") as font:
                font.write(b"fixture")
            result = self.invoke("--ignore-system-fonts", root=workspace)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("随附字体校验失败", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
