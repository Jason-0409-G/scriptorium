# Changelog

本插件遵循[语义化版本](https://semver.org/lang/zh-CN/)（`MAJOR.MINOR.PATCH`），版本号写在 `.claude-plugin/plugin.json` 的 `version`。**用户只在版本号 bump 时收到更新**；更新方式见 [README「更新」一节](README.md#更新)。

## [1.0.0] - 2026-06-25

首个带版本号的正式发布。**research-to-paper**：完全自包含的「研究 → 写作」流水线，7 个子 skill（scope / curate / write / audit / humanize / build + 主 skill），不依赖任何外部 skill。

### 检索与文献库（curate）
- 五源并检并去重：OpenAlex、Europe PMC、PubMed、Semantic Scholar、CrossRef。
- DOI 逐条对 CrossRef 交叉核验，抓死链与「张冠李戴」；并行 8 线程，支持 `--cache` 复用 / `--no-api` 离线；存在 mismatch/dead 时退出码非 0。
- 导出 RIS（Zotero/EndNote 通用）+ BibTeX + 分类彩色 Excel，每篇附一行**中文重点**与核验状态；可选直推 Zotero。
- 生物资源检索（`bio_search`）：NCBI Entrez 任意子库 + UniProt + RCSB PDB + AlphaFold + Europe PMC。
  - NCBI 命中 0 且含 CAZy 缩写（GH3 / CBM20…）时，自动展开为 NCBI 索引的全称（双拼法 OR）重查并透明提示。
  - AlphaFold 接受自由文本：经 UniProt 自动解析登录号，返回第一个有预测模型的候选。
  - UniProt 标题回退链（修 TrEMBL 条目空标题）；PDB 为所有返回条取标题。
  - HTTP 403/408/429 视为可重试（修连发限流导致的静默空结果）。
  - NCBI 自动放宽时读 `errorlist.phrasesnotfound` 并警告，不把无关结果当精确命中。

### 写作 / 审稿 / 去 AI / 排版
- **论证脉络矩阵 (argument-thread matrix)**：动笔前先锁「红线动机」并写明要论证 / 禁止论证（防各节漂移、防过度宣称），把每个最小写作单元逐行接到 动机链接 / 证据·引用锚 / 文字动作 三类锚 + 框架首行；配本地离线校验门 `research-to-paper-write/scripts/check_argument_matrix.py`（纯 stdlib、零联网，适配纯 DeepSeek 无 VPN），卡行数 / 字数 / 泛词黑名单 / 锚命中，未达标不许动笔；`new_workspace.py` 直接 seed 起手模板。
- 证据匹配的措辞（模型、基因层面只 predict，整体实测方 confirm）。
- 多个独立审稿主体对抗式复核；长短句去 AI；LaTeX / Word / PDF 输出。

### 其它
- DeepSeek 后端兼容；各 skill 自带触发评测集（`evals/trigger_evals.json`）。
