// 默认读取公开虚构示例；个人文件通过 --input content=... 显式选择。
#import "typst/template.typ": resume
#let language = sys.inputs.at("lang", default: "zh")
#assert(language in ("zh", "en"), message: "lang 可选 zh 或 en。")
#let settings-path = sys.inputs.at("settings", default: "resume/settings.toml")
#let default-content = if language == "en" { "resume/content.en.toml" } else { "resume/content.toml" }
#let content-path = sys.inputs.at("content", default: default-content)
#resume(toml(content-path), toml(settings-path))
