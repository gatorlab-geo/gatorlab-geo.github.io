import re
import os

# ── Lab Members ────────────────────────────────────────────────────────────────
# Add names here exactly as they appear in APA-rendered CSL output:
# "Last, F." — regex will match the full token.
# Supports both accented and unaccented variants (list both if needed).
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


def get_bib_key_order(bib_path: str) -> list[str]:
    """Return cite keys in the order they appear in the .bib file."""
    with open(bib_path, "r", encoding="utf-8") as f:
        content = f.read()
    return re.findall(r'@\w+\{(\w+)\s*,', content)


def reorder_entries(content: str, bib_keys: list[str]) -> str:
    """
    Reorder .csl-entry divs to match the reverse of the bib file order
    (last entry in bib appears first on the page).

    Quarto renders entries as siblings immediately after the #refs container div,
    not as children of it. The structure is:
      <div id="refs" ...></div>
      <div id="ref-key1" class="csl-entry" ...>...</div>
      <div id="ref-key2" class="csl-entry" ...>...</div>
      ...
      </div>  ← closing outer wrapper
    """
    # Match all csl-entry divs (single-line in Quarto's output)
    entry_pattern = re.compile(
        r'<div id="(ref-[^"]+)" class="csl-entry"[^>]*>.*?</div>',
        re.DOTALL
    )

    entries = {}  # ref-key -> full html
    for m in entry_pattern.finditer(content):
        entries[m.group(1)] = m.group(0)

    if not entries:
        return content

    # Build desired order: reverse of bib file (newest = first)
    desired_keys = [f"ref-{k}" for k in reversed(bib_keys)]
    ordered = [entries[k] for k in desired_keys if k in entries]
    # Append any entries not in the bib key list (defensive)
    for key, html in entries.items():
        if key not in desired_keys:
            ordered.append(html)

    # Replace the block of csl-entry divs with the reordered ones.
    # Find the span from the first to the last csl-entry div.
    first_match = entry_pattern.search(content)
    last_match = None
    for last_match in entry_pattern.finditer(content):
        pass

    if first_match is None or last_match is None:
        return content

    start = first_match.start()
    end = last_match.end()

    new_block = "\n".join(ordered)
    return content[:start] + new_block + content[end:]


def underline_lab_authors(content: str) -> str:
    """Wrap lab author name tokens inside .csl-entry divs with an underline span."""
    for name in LAB_AUTHORS:
        pattern = re.escape(name)
        replacement = f'<span style="{UNDERLINE_STYLE}">{name}</span>'
        safe_pattern = re.compile(r'(?<![>])' + pattern)
        content = safe_pattern.sub(replacement, content)
    return content


def fix_publications():
    if not os.path.exists(HTML_FILE):
        print(f"File not found: {HTML_FILE}")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Format DOI links
    doi_pattern = re.compile(r'<a href="https://doi\.org/([^"]+)">https://doi\.org/\1</a>')
    content = doi_pattern.sub(r'<a href="https://doi.org/\1">\1</a>', content)

    # 2. Format PDF links to icons
    def pdf_replacement(match):
        url = match.group(1)
        if "files/papers/" in url:
            file_name = url.split("files/papers/")[-1]
            url = "/files/papers/" + file_name
        return f' <a href="{url}" target="_blank" style="text-decoration: none;">[pdf]</a>'

    pdf_pattern = re.compile(r'<a href="([^"]+\.pdf)">([^<]+)</a>')
    content = pdf_pattern.sub(pdf_replacement, content)

    # 3. Reorder entries to match bib file order (last entry in bib = first on page)
    if os.path.exists(BIB_FILE):
        bib_keys = get_bib_key_order(BIB_FILE)
        content = reorder_entries(content, bib_keys)

    # 4. Underline lab authors
    content = underline_lab_authors(content)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Successfully processed {HTML_FILE}")


if __name__ == "__main__":
    fix_publications()
