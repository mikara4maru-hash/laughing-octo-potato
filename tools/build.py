"""問題データ（data/kanji-g3.json）を試作品のHTMLに埋め込み、先生確認用の問題一覧も作る。

使い方: python3 tools/build.py
出力:
  prototype/kanji-note-g3.html  … ブラウザで開くだけで動く試作品（1ファイル）
  docs/kanji-g3-questions.md    … 問題一覧（問題文・正答・解説・分類）
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data/kanji-g3.json").read_text(encoding="utf-8"))

# --- 試作品 ---
template = (ROOT / "src/app.html").read_text(encoding="utf-8")
embedded = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
out = ROOT / "prototype/kanji-note-g3.html"
out.parent.mkdir(exist_ok=True)
out.write_text(template.replace("/*__DATA__*/", embedded), encoding="utf-8")

# --- 問題一覧 ---
ranges = {r["id"]: r for r in data["ranges"]}
levels = {l["id"]: l["name"] for l in data["levels"]}
qs = data["questions"]
count = Counter((q["range"], q["level"]) for q in qs)

lines = [
    f"# {data['title']}",
    "",
    f"問題データ: `data/kanji-g3.json`（版: {data['version']}）。このファイルは `python3 tools/build.py` で自動生成しています。",
    "",
    "## 分類と問題数",
    "",
    "| 範囲 | 内容 | 解答の形 | " + " | ".join(levels.values()) + " | 計 |",
    "|---|---|---|" + "---:|" * (len(levels) + 1),
]
for r in data["ranges"]:
    n = [count[(r["id"], l)] for l in levels]
    form = "ひらがなで入力" if r["type"] == "read" else "選択肢から選ぶ"
    lines.append(f"| {r['name']} | {r['note']} | {form} | " + " | ".join(map(str, n)) + f" | {sum(n)} |")
total = [sum(count[(r['id'], l)] for r in data['ranges']) for l in levels]
lines.append("| 合計 | | | " + " | ".join(map(str, total)) + f" | {len(qs)} |")
lines += [
    "",
    "- 読みの問題は、ひらがな・カタカナ、全角・半角、空白の違いをそろえてから正答と比べる",
    "- 書きの問題は、かな漢字変換で答えが出てしまうため選択式にしている。選択肢は出題のたびに並べ替える",
    "- 例文はすべて自作",
    "",
]
for r in data["ranges"]:
    lines += [f"## {r['name']}", ""]
    if r["type"] == "read":
        lines += ["| ID | 難しさ | 問題文 | 正答 | 解説 |", "|---|---|---|---|---|"]
        for q in (q for q in qs if q["range"] == r["id"]):
            lines.append(f"| {q['id']} | {levels[q['level']]} | {q['sentence']} | {'・'.join(q['answers'])} | {q['explanation']} |")
    else:
        lines += ["| ID | 難しさ | 問題文 | 正答 | ほかの選択肢 | 解説 |", "|---|---|---|---|---|---|"]
        for q in (q for q in qs if q["range"] == r["id"]):
            others = "、".join(c for c in q["choices"] if c != q["answer"])
            lines.append(f"| {q['id']} | {levels[q['level']]} | {q['sentence']} | {q['answer']} | {others} | {q['explanation']} |")
    lines.append("")
(ROOT / "docs/kanji-g3-questions.md").write_text("\n".join(lines), encoding="utf-8")
print(f"built {out.relative_to(ROOT)} ({len(qs)} questions)")
