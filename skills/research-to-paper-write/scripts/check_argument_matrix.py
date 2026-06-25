#!/usr/bin/env python3
"""论证脉络矩阵 (argument-thread matrix) — 本地离线质量校验器.

把"写一篇有论证脉络的稿子"这个软目标编译成一组可逐行机械检查的硬约束,在动笔前卡住:
  1. 红线动机双向门: 文件顶部必须先锁定一句红线动机, 且同时写明「要论证」和「禁止论证」
     (后者防止后续各节漂成泛泛而谈 / 过度宣称).
  2. 论证脉络矩阵: 每个最小写作单元一行, 每行强制挂三类非空且具体的锚 ——
     动机链接 (这一行如何服务红线) / 证据·引用锚 (具体数据或某条文献) / 文字动作 (具体要做什么).
  3. 框架首行: 第一行论证整篇的控制结构, 必须是有内容的 design memo 而非一句话.
  4. 泛词黑名单: "提升清晰度 / 润色 / 更学术 / improve clarity / polish" 这类非理由直接判失败.
  5. 行数/字数下限: 防止用一两行糊弄.

纯标准库, 零网络调用, 不依赖任何大模型能力 —— 在纯 DeepSeek、无 VPN/代理的环境下可直接跑.
返回码: 全过 0; 有硬失败 1; 文件/表格找不到 2.

用法:
  python check_argument_matrix.py writing_rationale_matrix.md
  python check_argument_matrix.py writing_rationale_matrix.md --min-rows 12
"""
from __future__ import annotations
import argparse
import re
import sys
import unicodedata

# ── 列识别 (大小写、中英、列序均不敏感; 命中任一关键词即认定该列) ────────────────────
COLS = {
    "unit":      ["unit", "单元", "row id", "行号", "id"],
    "claim":     ["claim", "论点", "功能", "function"],
    "motivation":["motivation", "动机", "红线", "thread", "脉络"],
    "evidence":  ["evidence", "citation", "证据", "引用", "anchor", "锚", "数据"],
    "hedge":     ["hedge", "措辞", "强度"],
    "pattern":   ["pattern", "sota", "结构模式", "范文", "exemplar"],
    "move":      ["move", "text", "文字动作", "动作", "change", "改"],
    "check":     ["final", "落点", "检查", "check"],
}
# 必须每行非空且"具体"的三类锚
ANCHORS = ["motivation", "evidence", "move"]

PLACEHOLDERS = {"", "-", "—", "–", "n/a", "na", "tbd", "todo", "?", "??", "...", "…",
                "待定", "待填", "空", "略", "tba", "x"}

# 泛词黑名单: 整格内容基本就是这么一句"非理由"时判失败
GENERIC = [
    "improve clarity", "make academic", "make it academic", "more academic",
    "polish wording", "polish the wording", "polish", "add detail", "add details",
    "better flow", "improve flow", "fix grammar", "enhance readability", "general background",
    "background paragraph", "transition", "improve", "rephrase", "rewrite for clarity",
    "提升清晰度", "更清晰", "更学术", "更专业", "润色", "润色措辞", "增加细节", "丰富内容",
    "改善流畅", "优化措辞", "加强逻辑", "背景介绍", "背景段", "过渡", "承上启下",
    "调整语序", "让它更好", "完善", "优化", "改写", "重写一下",
]


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).strip()


def _visible_len(s: str) -> int:
    """字符数 (中文一字算一字; 去掉 markdown 强调符与多余空白)。"""
    s = re.sub(r"[*`_]+", "", s)
    return len(re.sub(r"\s+", "", s))


def parse_table(text: str):
    """抽出第一张 markdown 表格, 返回 (headers, rows[list[list[str]]])。无表返回 (None, [])。"""
    lines = text.splitlines()
    block = []
    for ln in lines:
        if ln.lstrip().startswith("|"):
            block.append(ln.strip())
        elif block:
            break  # 表格结束
    if len(block) < 3:
        return None, []

    def cells(row):
        parts = row.split("|")
        if parts and parts[0] == "":
            parts = parts[1:]
        if parts and parts[-1] == "":
            parts = parts[:-1]
        return [_norm(p) for p in parts]

    headers = cells(block[0])
    rows = [cells(r) for r in block[2:] if set(r.replace("|", "").strip()) - set("-: ")]
    return headers, rows


def map_columns(headers):
    """表头 → {语义键: 列索引}。"""
    idx = {}
    low = [h.lower() for h in headers]
    for key, kws in COLS.items():
        for i, h in enumerate(low):
            if any(kw in h for kw in kws):
                idx[key] = i
                break
    return idx


def is_placeholder(cell: str) -> bool:
    return _norm(cell).lower() in PLACEHOLDERS


def is_generic(cell: str) -> bool:
    c = _norm(cell).lower().rstrip("。.!！;；,，")
    if not c:
        return False
    for g in GENERIC:
        if c == g or (len(c) <= len(g) + 4 and c.startswith(g)) or (len(c) <= len(g) + 4 and c.endswith(g)):
            return True
    return False


def check_doublet(text: str):
    """红线动机双向门: 必须同时有「要论证」和「禁止论证」两侧, 且各自有实质内容。"""
    issues = []
    want_kw = ["要论证", "prioritized claim", "priorit", "to argue", "claims to make", "核心论点", "红线动机"]
    avoid_kw = ["禁止论证", "claims to avoid", "do not argue", "should not argue", "不论证", "不要论证", "避免宣称", "禁止宣称"]

    def side_present(keys):
        for kw in keys:
            m = re.search(re.escape(kw) + r"[^\n]*", text, re.IGNORECASE)
            if m:
                # 该标记同一行之后、或紧接下一非空行要有实质内容
                tail = m.group(0).split(kw, 1)[-1] if kw in m.group(0) else m.group(0)
                rest = text[m.end():]
                nxt = next((l for l in rest.splitlines() if l.strip()), "")
                if _visible_len(tail) >= 4 or _visible_len(nxt) >= 4:
                    return True
        return False

    if not side_present(want_kw):
        issues.append("缺「要论证」侧: 顶部红线动机里没写明本文的核心论点(优先论点)。")
    if not side_present(avoid_kw):
        issues.append("缺「禁止论证」侧: 没写明哪些是禁止论证/禁止宣称的(防漂移、防过度宣称的关键)。")
    return issues


def validate(text: str, min_rows: int, framework_floor: int):
    report = {"errors": [], "row_issues": [], "info": []}

    report["errors"].extend(check_doublet(text))

    headers, rows = parse_table(text)
    if headers is None:
        report["errors"].append("找不到矩阵表格(没有以 | 开头的 markdown 表)。")
        return report
    idx = map_columns(headers)
    missing_cols = [k for k in ANCHORS if k not in idx]
    if missing_cols:
        zh = {"motivation": "动机链接", "evidence": "证据/引用锚", "move": "文字动作"}
        report["errors"].append("表头缺必备锚列: " + ", ".join(zh[k] for k in missing_cols)
                                + f"  (现有表头: {headers})")
        return report

    if len(rows) < min_rows:
        report["errors"].append(f"行数 {len(rows)} < 下限 {min_rows}: 矩阵太薄, 一行≈一个最小写作单元, 整篇至少要 {min_rows} 行。")

    # 框架首行
    if rows:
        f = rows[0]
        ftotal = sum(_visible_len(c) for c in f)
        if ftotal < framework_floor:
            report["row_issues"].append((1, f"框架首行内容太少({ftotal}字 < {framework_floor}): 第一行要论证整篇控制结构, 写成 2-4 句的 design memo, 不是一句话。"))

    # 逐行锚检查
    for n, r in enumerate(rows, start=1):
        def cell(key):
            i = idx.get(key)
            return r[i] if i is not None and i < len(r) else ""
        for key in ANCHORS:
            zh = {"motivation": "动机链接", "evidence": "证据/引用锚", "move": "文字动作"}[key]
            v = cell(key)
            if is_placeholder(v):
                report["row_issues"].append((n, f"「{zh}」为空/占位: 每行都必须把这一行接到红线动机、具体证据、具体文字动作上。"))
            elif is_generic(v):
                report["row_issues"].append((n, f"「{zh}」是泛词「{v}」: 这不是理由。要写'为什么'和'怎么改的具体内容'。"))
            elif _visible_len(v) < 4 and key != "move":
                report["row_issues"].append((n, f"「{zh}」太短({v!r}): 写具体, 别只放关键词。"))
        # 论点列若存在也不能是泛词
        cl = cell("claim")
        if cl and is_generic(cl):
            report["row_issues"].append((n, f"「论点/功能」是泛词「{cl}」: 写它实际主张什么, 不是'背景段'这种标签。"))

    report["info"].append(f"表头识别: {[(k, headers[i]) for k, i in idx.items()]}")
    report["info"].append(f"数据行数: {len(rows)}")
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="论证脉络矩阵 (argument-thread matrix) 本地离线质量校验。")
    ap.add_argument("matrix", help="writing_rationale_matrix.md 路径")
    ap.add_argument("--min-rows", type=int, default=8, help="最少数据行数 (默认 8; 复杂论文常 20-60)")
    ap.add_argument("--framework-floor", type=int, default=180, help="框架首行最少可见字数 (默认 180)")
    args = ap.parse_args(argv)

    try:
        text = open(args.matrix, encoding="utf-8").read()
    except OSError as e:
        print(f"[matrix_check] 读不到文件 → {e}", file=sys.stderr)
        return 2

    rep = validate(text, args.min_rows, args.framework_floor)
    print("=== 论证脉络矩阵 校验 ===")
    for i in rep["info"]:
        print(f"  · {i}")
    hard = list(rep["errors"])
    if rep["errors"]:
        print("\n[结构性问题]")
        for e in rep["errors"]:
            print(f"  ✗ {e}")
    if rep["row_issues"]:
        print("\n[逐行问题]")
        for n, msg in rep["row_issues"]:
            print(f"  ✗ 行{n}: {msg}")
        hard.extend(rep["row_issues"])
    if not hard:
        print("\n✅ 通过: 红线动机双向齐全, 每行三类锚都具体, 行数达标。可以动笔。")
        return 0
    print(f"\n❌ 未通过: {len(rep['errors'])} 个结构性问题 + {len(rep['row_issues'])} 个逐行问题。先补齐再动笔。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
