# Clash AI 规则集 —— 最全合并版

⚙️ 由 GitHub Actions 每日 09:30（北京时间）自动重新合并上游数据并推送，订阅链接永久有效，无需手动维护。

## 订阅链接（jsDelivr 加速，国内可直连）

- 国外 AI 代理：`https://cdn.jsdelivr.net/gh/nori5555/clash-rules@main/AI_MERGED.list`
- 国内 AI 直连：`https://cdn.jsdelivr.net/gh/nori5555/clash-rules@main/AI_CN_DIRECT.list`
- raw 备用：`https://raw.githubusercontent.com/nori5555/clash-rules/main/AI_MERGED.list`

## 交付文件

| 文件 | 用途 |
|---|---|
| `AI_MERGED.list` | **国外 AI 代理规则**，265 个域名后缀（合并去重后），供 rule-provider `behavior: domain` 使用 |
| `AI_MERGED_RULES.txt` | 同上的规则行格式（`DOMAIN-SUFFIX,xxx,PROXY` + 7 个关键字规则），可直接粘贴进 rules |
| `AI_CN_DIRECT.list` | **国内 AI 直连清单**，116 个域名（DeepSeek/Kimi/通义/豆包/文心/智谱/混元…），用于 DIRECT |

## 覆盖范围（国外 AI，265 域名）

OpenAI / ChatGPT / Claude(Anthropic) / Google Gemini / Bard / GitHub Copilot / Microsoft Copilot / Perplexity / Poe / Groq / HuggingFace / Midjourney / Cursor / Windsurf / Cohere / ElevenLabs / Manus / xAI / Cerebras / Comfy 等全部主流 AI 服务。

## 数据源（上游，可持续更新）

| 来源 | 地址 | 特点 |
|---|---|---|
| **v2fly/domain-list-community**（geosite 底层） | `https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/category-ai-!cn` | 最权威的 AI 域名库，含 include 聚合 |
| **blackmatrix7/ios_rule_script** | `https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash/OpenAI/OpenAI.list`（Claude/Claude.list、Gemini/Gemini.list、Copilot/Copilot.list、BardAI/BardAI.list） | 条目细、更新勤 |
| **ACL4SSR/ACL4SSR** | `https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/AI.list`（另有 OpenAi/Claude/ClaudeAI/Gemini.list） | 手动聚合 |
| **MetaCubeX/meta-rules-dat**（mihomo 专用） | `https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ai-!cn.mrs` | 直接订阅 .mrs rule-set，单文件最省事 |

## Mihomo / Clash.Meta 配置示例

```yaml
rule-providers:
  ai-proxy:
    type: http
    behavior: domain
    format: text
    url: https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ai-!cn.mrs
    path: ./providers/ai-proxy.yaml
    interval: 86400
  ai-cn-direct:
    type: http
    behavior: domain
    format: text
    url: https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/meta/geo/geosite/category-ai-cn.mrs
    path: ./providers/ai-cn-direct.yaml
    interval: 86400

rules:
  # 国内 AI 优先直连（DeepSeek/Kimi/通义/豆包等）
  - RULE-SET,ai-cn-direct,DIRECT
  # 国外 AI 走代理
  - RULE-SET,ai-proxy,PROXY
  # ... 其他规则 ...
  - MATCH,DIRECT
```

> `.mrs` 是 mihomo 专用二进制规则集；老 Clash 内核用本目录的 `AI_MERGED.list`（text 格式）+ `behavior: domain`。
> 本仓库由 GitHub Actions 自动更新（`scripts/merge_ai_rules.py` + `.github/workflows/update-rules.yml`），每天 09:30 重新从上游合并。
