"""检查导出、预览和测试所需工具，以及当前字体设置与随附字体。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from check_original_fonts import FONT_EXPRESSION

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", default="resume/settings.toml")
    parser.add_argument("--ignore-system-fonts", action="store_true")
    parser.add_argument("--preview", action="store_true", help="要求 Tinymist 可用")
    parser.add_argument("--tests", action="store_true", help="要求测试所需 Poppler 工具可用")
    args = parser.parse_args(argv)
    failures = []
    print("Python " + sys.version.split()[0] + "（要求 3.9+）")
    if sys.version_info < (3, 9):
        failures.append("请安装 Python 3.9 或更新版本。")

    available = {}
    for name in ("make", "typst", "tinymist", "pdfinfo", "pdffonts", "pdftotext", "pdftoppm"):
        path = shutil.which(os.environ.get(name.upper(), name))
        required = name == "typst" or (args.preview and name == "tinymist") or (
            args.tests and name in ("make", "pdfinfo", "pdffonts", "pdftotext"))
        print(("OK " if path else "缺少 " if required else "可选，未安装 ") + name + (": " + path if path else ""))
        if path:
            available[name] = path
        elif required:
            failures.append("未找到 " + name + "；请参照 README 安装，或设置 " + name.upper() + " 可执行路径。")

    try:
        manifest = ROOT / "fonts/SHA256SUMS"
        for line in manifest.read_text().splitlines():
            expected, filename = line.split("  ", 1)
            if hashlib.sha256((ROOT / "fonts" / filename).read_bytes()).hexdigest() != expected:
                failures.append("随附字体校验失败：fonts/" + filename + "；请恢复原始字体文件。")
    except (OSError, ValueError) as error:
        failures.append("无法核验随附字体：" + str(error))

    if "typst" in available:
        try:
            settings = "/" + (ROOT / args.settings).resolve().relative_to(ROOT).as_posix()
            flags = ["--font-path", str(ROOT / "fonts")]
            if args.ignore_system_fonts:
                flags.append("--ignore-system-fonts")
            version = subprocess.run([available["typst"], "--version"], text=True, capture_output=True, check=True)
            print(version.stdout.strip() + "（本项目验证版本：0.15.1）")
            configured = subprocess.run(
                [available["typst"], "eval", "--root", str(ROOT), *flags, "--input", "settings-file=" + settings, FONT_EXPRESSION],
                cwd=ROOT, text=True, capture_output=True, check=True,
            )
            installed = subprocess.run([available["typst"], "fonts", *flags], text=True, capture_output=True, check=True)
            families = {line.strip().casefold() for line in installed.stdout.splitlines()}
            missing = [name for name in dict.fromkeys(json.loads(configured.stdout)) if name.casefold() not in families]
            if missing:
                failures.append("当前设置缺少字体：" + "、".join(missing) + "；请准备字体或修改 [fonts]。")
            else:
                print("OK 当前字体设置：" + args.settings)
        except ValueError:
            failures.append("字体设置文件必须位于项目根目录内，且 Typst 必须返回有效字体信息。")
        except (OSError, subprocess.CalledProcessError) as error:
            failures.append("无法检查字体：" + (getattr(error, "stderr", "") or str(error)).strip())

    if failures:
        for failure in failures:
            print("错误：" + failure, file=sys.stderr)
        return 1
    print("环境检查通过。预览需 Tinymist；测试需 Poppler，可用 --preview / --tests 强制检查。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
