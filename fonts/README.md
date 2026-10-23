# 字体

模板随附以下未修改字体，仅保留需要的字重；各字体使用自己的许可证，根目录 MIT 不替代字体授权。

| 目录 | 字体与字重 | 来源 | 许可证 |
| --- | --- | --- | --- |
| `SourceHanSerifCN/` | 思源宋体 Regular、Bold | [Adobe Source Han Serif](https://github.com/adobe-fonts/source-han-serif) | SIL OFL 1.1，见目录内许可证 |
| `SourceHanSansCN/` | 思源黑体 Regular、Bold | [Adobe Source Han Sans](https://github.com/adobe-fonts/source-han-sans) | SIL OFL 1.1，见目录内许可证 |
| `TeXGyreTermes/` | TeX Gyre Termes Regular、Bold | [CTAN TeX Gyre](https://ctan.org/pkg/tex-gyre) | GUST Font License，见许可证、README 与清单 |
| `Inter/` | Inter Variable | [Inter](https://github.com/rsms/inter) | SIL OFL 1.1，见目录内许可证 |

Typst 中的字体家族名分别为 `Source Han Serif`、`Source Han Sans`、`TeX Gyre Termes`、`Inter`。文件名中的 CN 不属于 Typst 家族名。

`SHA256SUMS` 记录本仓库随附字体文件的校验值。自备字体放在 `local/`，该目录被 Git 忽略；在 `resume/settings.toml` 的 `[fonts]` 中配置实际家族名。未随附商业字体与操作系统字体。原版预设由 `resume/settings.original.toml` 定义，使用 Adobe Song Std、Adobe Heiti Std、Helvetica Neue，须由用户将有授权的字体放入忽略的 `local/` 或安装到系统，不能提交这些文件。

思源黑体原始字体下载路径：

- [Regular](https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/SubsetOTF/CN/SourceHanSansCN-Regular.otf)
- [Bold](https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/SubsetOTF/CN/SourceHanSansCN-Bold.otf)

字体文件保持原样，不做子集化或重命名字体内部名称；PDF 中的嵌入子集由 Typst 生成。自制文字徽标使用思源黑体生成矢量轮廓，源脚本位于 `scripts/generate_badges.py`。
