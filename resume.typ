// 同一入口选择语言和字体预设；两份内容都仅包含虚构示例。
#import "typst/template.typ": resume
#let language = sys.inputs.at("lang", default: "zh")
#assert(language in ("zh", "en"), message: "lang 可选 zh 或 en。")
#let settings-path = sys.inputs.at("settings", default: "resume/settings.toml")
#let content-path = if language == "en" { "resume/content.en.toml" } else { "resume/content.toml" }
#resume(toml(content-path), toml(settings-path))
