# research-to-paper

> [English](README.en.md) ｜ 中文

一套**完全自包含**的学术写作技能(skill):把一个研究想法,一路带到投稿就绪的稿件——从**定方向**、到**核对过 DOI 的文献库**、到**起草+多轮审稿+去AI**、再到 **LaTeX / Word / PDF** 输出。**不依赖任何其它 skill**:装这一个插件,整条流水线就都有了。

适用于 **Claude Code** 与 **Codex**。

---

## 安装

### Claude Code

**方式一 · 插件市场(推荐)**

```
/plugin marketplace add Jason-0409-G/skill_writing
/plugin install research-to-paper@skill-writing
/reload-plugins
```

**方式二 · 脚本(克隆后本地装)**

```bash
git clone https://github.com/Jason-0409-G/skill_writing.git
cd skill_writing
bash install.sh claude          # macOS / Linux
# Windows PowerShell:  .\install.ps1 -Target claude
```
装好后**重启 Claude Code**,直接让它"按 research-to-paper 的流程做"即可。

### Codex

```bash
git clone https://github.com/Jason-0409-G/skill_writing.git
cd skill_writing
bash install.sh codex           # macOS / Linux
# Windows PowerShell:  .\install.ps1 -Target codex
```
脚本会把 7 个 skill 拷进 `~/.codex/skills/`(Claude 则是 `~/.claude/skills/`)。**重启 Codex** 后即可使用。`bash install.sh all` 可一次装两个。

---

## 七个子 skill 各干什么

| 子 skill | 用途 |
|---|---|
| **research-to-paper** | 主编排。判断你在哪一步,按需把请求走过 **定方向 → 建库 → 写 → 排版**,各步独立可用。 |
| **research-to-paper-scope** | **定方向**。先检索权威文献把领域搞懂,再**一问一确认**:角度/研究问题 → 范围 → **目标期刊** → **字数** → 核心子主题;期刊一旦定下,**联网查它的投稿要求**(scope、文章类型、长度、结构、引用格式)。产出 `scope_brief.md`。 |
| **research-to-paper-curate** | **建文献库**。五源检索(OpenAlex / Europe PMC / PubMed / Semantic Scholar / Crossref)→ 逐篇 **CrossRef 核对 DOI**(连"能解析但指向错论文"都逮、并找回正确 DOI)→ **多 agent 对抗审查**剔除伪造/张冠李戴 → 导出 **RIS(Zotero/EndNote 通用)+ BibTeX + 按主题着色的 Excel**。 |
| **research-to-paper-write** | **写作**。先理解内容、复述核心论点跟你确认 → 列**逐单元 rationale 矩阵**(不套 IMRaD 模板)→ 按**证据对冲**起草(模型/基因只能 predict、整体实测才能 confirm);并编排下面的审稿与去AI。三版本:综述 / 报告 / 论文。 |
| **research-to-paper-audit** | **多轮对抗审稿**。派 **3 个互相独立的审稿 agent**(claim 支撑 / 逻辑结构 / 引用证据)+ 主编综合,**审到一轮干净为止**;专逮过度声称、无据 claim、结果区混入解读、浅改、引用支撑不住。可单独调用("审一下这篇")。 |
| **research-to-paper-humanize** | **去 AI / 降 AI 率**。按**五个维度**改:**D1 句长(长短句结合)**、D2 段落结构变化、D3 信息密度起伏、D4 连接词控制(删"首先/此外/值得注意的是"等)、D5 术语变体;分 light/medium/heavy 三档,每处改动记进 `humanize_matrix.md`,再用 `humanize_check.py` **量化校验**。可单独调用("把这段降AI率")。 |
| **research-to-paper-build** | **出格式**。用 pandoc 把定稿渲染成 **LaTeX(.tex)/ Word(.docx)/ PDF**,并把 `[@key]` 引用按 `library.bib` 解析成参考文献表。 |

每一块都能**单独触发**:"核对这些 DOI""降AI率这段""审一下草稿""导出成 Word"都会直接命中对应 skill。

---

## 依赖

除以下可选工具外,全部是 Python **标准库**(缺了会优雅降级或提示):

- **`openpyxl`**(Python)— 着色 `.xlsx`;没有则 curate 改写 `.csv`,RIS/BibTeX 不受影响。
- **`pandoc`** — `research-to-paper-build` 出 LaTeX/Word 必需(`brew install pandoc` / `apt install pandoc` / Windows 用 winget/choco)。
- **TeX 引擎**(xelatex/pdflatex)— 仅 PDF 需要;没有也照出 `.tex`,可拿到别处编译。
- 设 **`CROSSREF_MAILTO`** / **`NCBI_EMAIL`** 为你的邮箱,API 会把你放进更快的 polite 池。

---

## 用法举例

直接说就行,例如:

- "我有个研究方向但还没定题——先帮我把方向和切入点定下来,查权威文献、核对 DOI,再写成综述。"
- "把这批参考文献核对一下 DOI、剔掉假的,导成能进 EndNote 的库。"
- "把这段降一下 AI 率,长短句结合。" ／ "审一下这篇草稿有没有过度声称。"
- "把这个稿子导出成 LaTeX 和 Word。"

主编排只跑你需要的那几步,并在进入下一步前告诉你每步产出了什么。

---

## 校验(改完插件后)

```
claude plugin validate .
```
