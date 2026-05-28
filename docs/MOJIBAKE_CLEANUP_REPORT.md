# 中文乱码清理审计报告

- 测试时间：2026-05-28 09:51:53
- 扫描根目录：`D:\codex2_cataSi-O`
- 扫描文本文件数：354
- 活动文件疑似乱码行数：0
- 归档/来源目录疑似乱码行数：16

## 判定规则

本审计查找常见 UTF-8/GBK 误解码痕迹，例如 `Ã`、`Â`、`â`、`Î`、`Ï`、`鏂`、`璁`、`鐢`、`鈥` 等。合法科研符号如 Δ、β、π、ρ、∇、Å、→、← 不计为乱码。

## 活动文件待清理项

未发现活动文件中的疑似乱码。

## 归档/来源目录记录

- `integrated/origin-frontend/config/build2.txt:1`：`��`
- `integrated/origin-frontend/config/build2.txt:9`：`\0 \0 \0;�?\0N\0e\0x\0t\0.\0j\0s\0 \01\04\0.\02\0.\03\05\0`
- `integrated/origin-frontend/config/build2.txt:15`：`\0 \0A�?\0C\0o\0m\0p\0i\0l\0e\0d\0 \0s\0u\0c\0c\0e\0s\0s\0f\0u\0l\0l\0y\0`
- `integrated/origin-frontend/config/build2.txt:23`：`\0n\0o\0d\0e\0.\0e\0x\0e\0 \0:\0 \0 \0?�?\0U\0s\0i\0n\0g\0 \0e\0d\0g\0e\0 \0r\0u\0n\0t\0i\0m\0e\0 \0o\0n\0 \0a\0 \0p\0a\0g\0e\0 \0c\0u\0r\0r\0e\0n\0t\0l\0y\0 \0d\0i\0s\0a\0b\0l\0e\0s\0 \0s\0t\0a\0t\0i\0c\0 \0g\0e\0n\0e\0r\0a\0t\0i\0o\0n\0 \0f\0o\0r\0 \0t\0h\0a\0t\0...`
- `integrated/origin-frontend/config/build2.txt:25`：`\0@b(WMOn \0L�:\01\0 \0W[&{:\0 \01\0`
- `integrated/origin-frontend/config/build2.txt:31`：`\0 \0 \0 \0 \0+\0 \0C\0a\0t\0e\0g\0o\0r\0y\0I\0n\0f\0o\0 \0 \0 \0 \0 \0 \0 \0 \0 \0 \0:\0 \0N\0o\0t\0S\0p\0e\0c\0i\0f\0i\0e\0d\0:\0 \0(\0 \0?�?\0U\0s\0i\0n\0g\0 \0e\0d\0g\0e\0 \0r\0.\0.\0.\0n\0 \0f\0o\0r\0 \0t\0h\0a\0t\0 \0p\0a\0g\0e\0:\0S\0t\0r\0i\0n\0g\0)\0 \0[\0...`
- `integrated/origin-frontend/config/build2.txt:247`：`\0 \0A�?\0G\0e\0n\0e\0r\0a\0t\0i\0n\0g\0 \0s\0t\0a\0t\0i\0c\0 \0p\0a\0g\0e\0s\0 \0(\03\00\0/\03\00\0)\0`
- `integrated/origin-frontend/config/build_output.txt:1`：`��`
- `integrated/origin-frontend/config/build_output.txt:9`：`\0 \0 \0;�?\0N\0e\0x\0t\0.\0j\0s\0 \01\04\0.\02\0.\03\05\0`
- `integrated/origin-frontend/config/build_output.txt:15`：`\0 \0A�?\0C\0o\0m\0p\0i\0l\0e\0d\0 \0s\0u\0c\0c\0e\0s\0s\0f\0u\0l\0l\0y\0`
- `integrated/origin-frontend/config/build_output.txt:23`：`\0n\0o\0d\0e\0.\0e\0x\0e\0 \0:\0 \0 \0?�?\0U\0s\0i\0n\0g\0 \0e\0d\0g\0e\0 \0r\0u\0n\0t\0i\0m\0e\0 \0o\0n\0 \0a\0 \0p\0a\0g\0e\0 \0c\0u\0r\0r\0e\0n\0t\0l\0y\0 \0d\0i\0s\0a\0b\0l\0e\0s\0 \0s\0t\0a\0t\0i\0c\0 \0g\0e\0n\0e\0r\0a\0t\0i\0o\0n\0 \0f\0o\0r\0 \0t\0h\0a\0t\0...`
- `integrated/origin-frontend/config/build_output.txt:25`：`\0@b(WMOn \0L�:\01\0 \0W[&{:\0 \01\0`
- `integrated/origin-frontend/config/build_output.txt:31`：`\0 \0 \0 \0 \0+\0 \0C\0a\0t\0e\0g\0o\0r\0y\0I\0n\0f\0o\0 \0 \0 \0 \0 \0 \0 \0 \0 \0 \0:\0 \0N\0o\0t\0S\0p\0e\0c\0i\0f\0i\0e\0d\0:\0 \0(\0 \0?�?\0U\0s\0i\0n\0g\0 \0e\0d\0g\0e\0 \0r\0.\0.\0.\0n\0 \0f\0o\0r\0 \0t\0h\0a\0t\0 \0p\0a\0g\0e\0:\0S\0t\0r\0i\0n\0g\0)\0 \0[\0...`
- `integrated/origin-frontend/config/build_output.txt:337`：`\0 \0A�?\0G\0e\0n\0e\0r\0a\0t\0i\0n\0g\0 \0s\0t\0a\0t\0i\0c\0 \0p\0a\0g\0e\0s\0 \0(\03\00\0/\03\00\0)\0`
- `integrated/origin-frontend/config/playwright-report/index.html:18`：`*/var y1;function pA(){if(y1)return vi;y1=1;var i=Symbol.for("react.transitional.element"),u=Symbol.for("react.fragment");function c(f,r,o){var h=null;if(o!==void 0&&(h=""+o),r....`
- `integrated/origin-frontend/config/tsc_errors.txt:1`：`��s\0r\0c\0/\0a\0p\0p\0/\0c\0h\0a\0r\0g\0e\0-\0p\0o\0p\0u\0l\0a\0t\0i\0o\0n\0/\0p\0a\0g\0e\0.\0t\0s\0x\0(\01\06\00\0,\03\0)\0:\0 \0e\0r\0r\0o\0r\0 \0T\0S\01\01\02\08\0:\0 \0D\0e\0c\0l\0a\0r\0a\0t\0i\0o\0n\0 \0o\0r\0 \0s\0t\0a\0t\0e\0m\0e\0n\0t\0 \0e\0x\0p\0e\0c\0t...`

## 清理边界

- 活动源码、测试、脚本、README、CHANGELOG 和当前 docs 应优先修复。
- `integrated/origin-*` 与 `docs/merged-from-si-o` 视为来源归档，默认只记录，不参与生产构建修复。
- 若乱码出现在测试断言中，必须同步修复后端/API 返回文本，不能只改测试。
