"""根据实际设置检查原版预设字体，避免发生静默回退。"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FONT_EXPRESSION = '''{
  import "/typst/template.typ": resolve-fonts;
  let fonts = resolve-fonts(toml(sys.inputs.at("settings-file")));
  ("body", "heading", "contact").map(key => fonts.at(key)).flatten()
}'''


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", default="resume/settings.original.toml")
    parser.add_argument("--ignore-system-fonts", action="store_true")
    args = parser.parse_args(argv)
    tool = os.environ.get("TYPST", "typst")
    settings = (ROOT / args.settings).resolve()
    try:
        # Typst 的绝对路径相对于项目根目录，而非操作系统根目录。
        settings_input = "/" + settings.relative_to(ROOT).as_posix()
    except ValueError:
        sys.exit("字体设置文件必须位于项目根目录内。")
    font_flags = ["--font-path", str(ROOT / "fonts")]
    if args.ignore_system_fonts:
        font_flags.append("--ignore-system-fonts")
    try:
        configured = subprocess.run(
            [tool, "eval", "--root", str(ROOT), *font_flags,
             "--input", "settings-file=" + settings_input, FONT_EXPRESSION],
            cwd=ROOT, text=True, capture_output=True, check=True,
        )
        required = list(dict.fromkeys(json.loads(configured.stdout)))
        installed = subprocess.run(
            [tool, "fonts", *font_flags], cwd=ROOT,
            text=True, capture_output=True, check=True,
        )
    except FileNotFoundError:
        sys.exit("未找到 Typst，请安装 Typst 或通过 TYPST 指定可执行文件。")
    except subprocess.CalledProcessError as error:
        sys.exit(error.stderr.strip() or "无法读取字体设置或字体列表。")
    available = {name.strip().casefold() for name in installed.stdout.splitlines()}
    missing = [name for name in required if name.casefold() not in available]
    if missing:
        sys.exit("原版字体未备齐：" + "、".join(missing)
                 + "。请将有授权的字体放入 fonts/local/ 或安装到系统；开源字体版请运行 make。")


if __name__ == "__main__":
    main()
