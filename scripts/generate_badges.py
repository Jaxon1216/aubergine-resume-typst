"""重新生成自制文字徽标，需 Typst；不使用外部角色图片。"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BADGES = (
    ("chii", "吉", "#fff0ed", "#bb6b71"),
    ("hachi", "哈", "#eaf2ff", "#567fae"),
    ("usa", "乌", "#fff6d5", "#a8843e"),
)


def main():
    (ROOT / "tmp").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="badges-", dir=ROOT / "tmp") as directory:
        for name, label, background, foreground in BADGES:
            source = Path(directory) / (name + ".typ")
            source.write_text(
                '#set page(width: 24pt, height: 24pt, margin: 0pt, fill: none)\n'
                '#set text(font: "Source Han Sans", size: 14pt, weight: "bold", '
                'top-edge: "bounds", bottom-edge: "bounds")\n'
                '#block(width: 24pt, height: 24pt, radius: 7pt, '
                f'fill: rgb("{background}"))[\n'
                f'  #align(center + horizon)[#text(fill: rgb("{foreground}"))[{label}]]\n'
                ']\n', encoding="utf-8",
            )
            subprocess.run([
                "typst", "compile", "--root", str(ROOT), "--font-path", str(ROOT / "fonts"),
                "--ignore-system-fonts", str(source),
                str(ROOT / "resume/assets/logos" / (name + ".svg")),
            ], cwd=ROOT, check=True)
    print("Generated three original text badges.")


if __name__ == "__main__":
    main()
