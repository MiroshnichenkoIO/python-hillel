"""Збірка PDF-конспектів з markdown-файлів уроку.

Використання:
    python md2pdf.py "d:/PY/Урок 2" out_dir

Кроки: markdown -> html (з CSS для друку A4) -> pdf через headless Chrome.
"""

import re
import subprocess
import sys
from pathlib import Path

from markdown_it import MarkdownIt

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = """
@page { size: A4; margin: 18mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Verdana, Arial, sans-serif; font-size: 11.5pt;
       line-height: 1.55; color: #1b1b1f; margin: 0; }
h1 { font-size: 24pt; margin: 0 0 14pt; color: #14532d; }
h2 { font-size: 16pt; margin: 20pt 0 8pt; padding-bottom: 4pt;
     border-bottom: 2px solid #86efac; color: #14532d; page-break-after: avoid; }
h3 { font-size: 13pt; margin: 14pt 0 6pt; color: #166534; page-break-after: avoid; }
p { margin: 6pt 0; }
ul, ol { margin: 6pt 0 6pt 18pt; padding: 0; }
li { margin: 3pt 0; }
code { font-family: Consolas, "Courier New", monospace; font-size: 10pt;
       background: #f1f5f9; padding: 1pt 4pt; border-radius: 3px; }
pre { font-family: Consolas, "Courier New", monospace; font-size: 9.5pt;
      background: #0f172a; color: #e2e8f0; padding: 9pt 11pt; border-radius: 6px;
      line-height: 1.45; white-space: pre-wrap; page-break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; font-size: 9.5pt; }
table { border-collapse: collapse; width: 100%; margin: 10pt 0; font-size: 10.5pt;
        page-break-inside: avoid; }
th, td { border: 1px solid #d1d5db; padding: 5pt 8pt; text-align: left; vertical-align: top; }
th { background: #dcfce7; }
blockquote { margin: 10pt 0; padding: 8pt 12pt; background: #eff6ff;
             border-left: 4px solid #3b82f6; }
a { color: #1d4ed8; text-decoration: none; }
hr { border: none; border-top: 1px solid #d1d5db; margin: 14pt 0; }
footer { margin-top: 20pt; font-size: 9.5pt; color: #6b7280;
         border-top: 1px solid #d1d5db; padding-top: 6pt; }
"""

TEMPLATE = """<!doctype html>
<html lang="uk"><head><meta charset="utf-8"><title>{title}</title>
<style>{css}</style></head><body>
{body}
<footer>{footer}</footer>
</body></html>
"""


def md_to_html(md_path: Path, title: str, footer: str) -> str:
    """Перетворити markdown-файл на готовий до друку HTML."""
    md = MarkdownIt("commonmark").enable("table").enable("strikethrough")
    body = md.render(md_path.read_text(encoding="utf-8"))
    # посилання на .md всередині PDF не працюють — прибираємо розширення
    body = re.sub(r'href="([^"]+)\.md(#[^"]*)?"', r'href="\1"', body)
    return TEMPLATE.format(title=title, css=CSS, body=body, footer=footer)


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    """Надрукувати HTML у PDF через headless Chrome."""
    subprocess.run(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    """Зібрати PDF для кожного markdown-файла уроку."""
    lesson_dir = Path(sys.argv[1])
    work_dir = Path(sys.argv[2])
    work_dir.mkdir(parents=True, exist_ok=True)

    titles = {
        "01_teoriya": "Урок 2 - Git, GitHub, GitLab (теорія)",
        "02_nalashtuvannya": "Урок 2 - Встановлення та налаштування Git",
        "03_robota_z_failamy": "Урок 2 - Робота з файлами (add, commit, log, diff)",
        "04_github_ssh": "Урок 2 - GitHub і SSH-ключі",
        "05_gitlab": "Урок 2 - GitLab",
        "06_branches_pr_merge": "Урок 2 - Гілки, Pull Request, Merge",
        "07_korysni_fishky": "Урок 2 - Корисні фішки Git",
        "GIT_CHEATSHEET": "Урок 2 - Шпаргалка Git",
        "practice/PRACTICE": "Урок 2 - Практика",
        "homework/HOMEWORK": "Урок 2 - Домашнє завдання",
    }
    footer = "Урок 2 · курс Python · повний набір матеріалів — у папці «Урок 2»"

    for stem, title in titles.items():
        md_path = lesson_dir / f"{stem}.md"
        if not md_path.exists():
            print(f"пропущено (немає файлу): {md_path}")
            continue
        safe = stem.replace("/", "_")
        html_path = work_dir / f"{safe}.html"
        pdf_tmp = work_dir / f"{safe}.pdf"
        html_path.write_text(md_to_html(md_path, title, footer), encoding="utf-8")
        html_to_pdf(html_path, pdf_tmp)
        target = lesson_dir / f"{title}.pdf"
        target.write_bytes(pdf_tmp.read_bytes())
        print(f"готово: {target.name} ({target.stat().st_size // 1024} КБ)")


if __name__ == "__main__":
    main()
