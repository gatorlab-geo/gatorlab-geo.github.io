import re
import os

def fix_publications():
    file_path = "docs/publications.html"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. format DOI links
    # Search for: <a href="https://doi.org/(DOI)">https://doi.org/(DOI)</a>
    # Replace with: <a href="https://doi.org/\1">\1</a>
    # We use a non-greedy match for the href and content
    doi_pattern = re.compile(r'<a href="https://doi\.org/([^"]+)">https://doi\.org/\1</a>')
    content = doi_pattern.sub(r'<a href="https://doi.org/\1">\1</a>', content)

    # 2. Format PDF links to icons
    # Search for: <a href="(...pdf)">...pdf</a>
    # Note: The CSL output usually makes the link text equal to the URL.
    # We want to replace the text with an icon.
    # Pattern: <a href="(any string ending in .pdf)">same string</a>
    # But CSL might escape things, so we should be careful.
    # Let's just find any anchor where href ends in .pdf.
    
    def pdf_replacement(match):
        url = match.group(1)
        # Content is match.group(2) - we ignore it and use the icon
        # Strip potential erroneous "https://" from local file paths (if Pandoc added it)
        # If the url starts with "https://files/", replace with "/files/"
        if "files/papers/" in url:
            # Aggressively clean the URL to ensure it is a root-relative path
            # Split by "files/papers/" and take the last part
            file_name = url.split("files/papers/")[-1]
            url = "/files/papers/" + file_name

        # User requested simple text "[pdf]" to avoid alignment issues
        return f' <a href="{url}" target="_blank" style="text-decoration: none;">[pdf]</a>'

    # Regex matches: <a href="...pdf"...>...</a>
    # We assume the href is roughly the first attribute or we scan for it.
    # Simple approach: <a href="([^"]+\.pdf)">([^<]+)</a>
    pdf_pattern = re.compile(r'<a href="([^"]+\.pdf)">([^<]+)</a>')
    content = pdf_pattern.sub(pdf_replacement, content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Successfully processed {file_path}")

if __name__ == "__main__":
    fix_publications()
