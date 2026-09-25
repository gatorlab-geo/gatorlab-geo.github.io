import re
import os

LAB_AUTHORS = [
    "Juhász, L.",
    "Juhasz, L.",
    "Davenport, P.",
]

UNDERLINE_STYLE = (
    'text-decoration: underline; '
    'text-underline-offset: 3px;'
)

BIB_FILE = "references.bib"
HTML_FILE = "docs/publications.html"

def get_bib_entries(bib_path: str):
    """Return cite keys and years in the order they appear in the .bib file."""
    with open(bib_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    entries = []
    blocks = content.split('@')[1:]
    for block in blocks:
        m_key = re.match(r'\w+\{([^,]+),', block)
        if not m_key: continue
        key = m_key.group(1).strip()
        
        m_year = re.search(r'year\s*=\s*[\{"]?(\d{4})', block, re.IGNORECASE)
        year = m_year.group(1) if m_year else "Unknown"
        entries.append((key, year))
    return entries

def reorder_entries(content: str, bib_entries: list) -> str:
    entry_pattern = re.compile(
        r'<div id="(ref-[^"]+)" class="csl-entry"[^>]*>.*?</div>',
        re.DOTALL
    )

    html_entries = {}
    for m in entry_pattern.finditer(content):
        html_entries[m.group(1)] = m.group(0)

    if not html_entries:
        return content

    by_year = {}
    for key, year in reversed(bib_entries):
        html_key = f"ref-{key}"
        if html_key in html_entries:
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(html_entries[html_key])

    sorted_years = sorted(by_year.keys(), reverse=True)
    
    new_blocks = []
    for year in sorted_years:
        new_blocks.append(f"<h2 style='margin-top: 30px;'>{year}</h2>")
        new_blocks.append("<ol style='margin-left: 20px;'>")
        for html in by_year[year]:
            # Remove any specific margin/indent from csl-entry so it behaves well in <ol>
            html = re.sub(r'class="csl-entry"', 'class="csl-entry" style="margin-left: 0; text-indent: 0; margin-bottom: 1em;"', html)
            new_blocks.append(f"<li>{html}</li>")
        new_blocks.append("</ol>")

    first_match = entry_pattern.search(content)
    last_match = None
    for last_match in entry_pattern.finditer(content):
        pass

    if first_match is None or last_match is None:
        return content

    start = first_match.start()
    end = last_match.end()

    new_block_str = "\n".join(new_blocks)
    
    content = content[:start] + new_block_str + content[end:]
    
    # Remove hanging-indent class from parent div if exists
    content = content.replace('hanging-indent', '')
    
    return content

def underline_lab_authors(content: str) -> str:
    for name in LAB_AUTHORS:
        pattern = re.escape(name)
        replacement = f'<span style="{UNDERLINE_STYLE}">{name}</span>'
        safe_pattern = re.compile(r'(?<![>])' + pattern)
        content = safe_pattern.sub(replacement, content)
    return content

def fix_publications():
    if not os.path.exists(HTML_FILE):
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    doi_pattern = re.compile(r'<a href="https://doi\.org/([^"]+)">https://doi\.org/\1</a>')
    content = doi_pattern.sub(r'<a href="https://doi.org/\1">\1</a>', content)

    def pdf_replacement(match):
        url = match.group(1)
        if "files/papers/" in url:
            file_name = url.split("files/papers/")[-1]
            url = "/files/papers/" + file_name
        return f' <a href="{url}" target="_blank" style="text-decoration: none;">[pdf]</a>'

    pdf_pattern = re.compile(r'<a href="([^"]+\.pdf)">([^<]+)</a>')
    content = pdf_pattern.sub(pdf_replacement, content)

    if os.path.exists(BIB_FILE):
        bib_entries = get_bib_entries(BIB_FILE)
        content = reorder_entries(content, bib_entries)

    content = underline_lab_authors(content)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    fix_publications()
