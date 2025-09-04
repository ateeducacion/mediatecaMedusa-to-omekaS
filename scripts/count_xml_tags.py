#!/usr/bin/env python3
"""
count_xml_tags.py

Reads a CSV file listing URLs (XML feeds) and counts specific XML elements in each retrieved XML document.

Updated behavior:
- If you provide --xml-dir, the script will read XML content from files located in that directory.
  The final component of each URL (the last path segment) is treated as the XML filename.
  For example, URL "http://example.com/path/to/file.xml" will map to "<xml-dir>/file.xml".
- If --xml-dir is not provided, the script keeps the original behavior and fetches the XML from the given URL.

Counts performed:
- attachment_root_items: number of <item> elements with <wp:post_type>=attachment and <wp:post_parent>=0
- attachment_items: number of <item> elements with <wp:post_type>=attachment
- media_category_terms: number of <wp:term_taxonomy><![CDATA[media-category]]></wp:term_taxonomy> occurrences

Output:
- A CSV file with columns: numero, nombre, url, attachment_root_items, attachment_items, media_category_terms, error (empty if no error)

Usage:
- python3 scripts/count_xml_tags.py
  (uses default input: exports/mediatecas.csv, output: exports/medias_xml_tag_counts.csv)

- You can override input/output with command line options:
  -i/--input <path_to_csv>
  -o/--output <path_to_csv>
  -c/--column <url_column_name> (optional)
  --nombre <nombre_column_name> (optional)
  -d/--xml-dir <path_to_xml_directory> (optional; enables local file mode)
  -t/--timeout <seconds> (HTTP request timeout; default 20)
  --retries <int> (HTTP retry attempts; default 3)
  --backoff <float> (Backoff factor for retries; default 0.3)

Notes:
- This script uses requests to fetch XML content when not reading from a directory.
- When reading from a directory, errors reading a file (not found, decode errors) are captured in the error field.
"""

import argparse
import csv
import re
import requests
import sys
import os
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries(retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    """
    Create a requests Session configured with a retry strategy.
    Retries on server errors (5xx) and certain connection issues.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD", "OPTIONS"])
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def detect_url_column(header: list) -> str:
    # Prefer a column literally named 'url', or a column that clearly contains URLs
    if not header:
        return ""
    for name in header:
        low = name.lower()
        if low == "url" or low.endswith("url") or "url" in low:
            return name
    # Fallback: first column
    return header[0]

def detect_nombre_column(header: list) -> str:
    # Prefer a column literally named 'nombre' (or 'name' if Spanish column missing)
    if not header:
        return ""
    for name in header:
        low = name.lower()
        if low == "nombre" or low == "name" or "nombre" in low:
            return name
    return ""


def fetch_xml(url: str, timeout: int, session: requests.Session) -> str:
    headers = {
        "User-Agent": "MediatecaTagCounter/1.0 (+https://example.invalid/)"
    }
    resp = session.get(url, timeout=timeout, headers=headers)
    resp.raise_for_status()
    return resp.text

def read_xml_from_dir(filename: str, xml_dir: str) -> str:
    """
    Read XML content from a local file located in xml_dir with the given filename.
    """
    path = os.path.join(xml_dir, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    return os.path.basename(parsed.path)

def count_tags(xml_text: str) -> tuple:
    """
    Count occurrences of:
    - <item ...> tags with <wp:post_type>=attachment and <wp:post_parent>=0 (attachment_root_items)
    - <item ...> tags with <wp:post_type>=attachment (attachment_items)
    - <wp:term_taxonomy><![CDATA[media-category]]></wp:term_taxonomy> occurrences (media_category_terms)
    - Extract the date from <wp:post_date> tag for each item
    The counts are performed on the raw XML string to avoid namespace parsing issues.
    """
    
    # Count items with wp:post_type=attachment and wp:post_parent=0
    # We need to find <item> blocks that contain both conditions
    attachment_root_items = 0
    attachment_items = 0
    
    # Find all <item> blocks
    item_pattern = r'<item\b[^>]*>.*?</item>'
    item_blocks = re.findall(item_pattern, xml_text, flags=re.IGNORECASE | re.DOTALL)
    
    for item_block in item_blocks:
        # Check if this item has wp:post_type with attachment (handle CDATA)
        post_type_pattern = r'<wp:post_type\b[^>]*>\s*(?:<!\[CDATA\[)?\s*attachment\s*(?:\]\]>)?\s*</wp:post_type>'
        if re.search(post_type_pattern, item_block, flags=re.IGNORECASE):
            attachment_items += 1
            
            # Also check if wp:post_parent=0 (no CDATA for numbers)
            post_parent_pattern = r'<wp:post_parent\b[^>]*>\s*0\s*</wp:post_parent>'
            if re.search(post_parent_pattern, item_block, flags=re.IGNORECASE):
                attachment_root_items += 1
    
    # Count wp:term_taxonomy with media-category (exact CDATA format)
    media_category_pattern = r'<wp:term_taxonomy\b[^>]*>\s*<!\[CDATA\[media-category\]\]>\s*</wp:term_taxonomy>'
    media_category_matches = re.findall(media_category_pattern, xml_text, flags=re.IGNORECASE | re.DOTALL)
    media_category_terms = len(media_category_matches)
    
    # Extract the date from the last attachment item's post_date tag
    post_date = ""
    # Filter item blocks to only include those with post_type=attachment
    attachment_items_blocks = []
    for item_block in item_blocks:
        post_type_pattern = r'<wp:post_type\b[^>]*>\s*(?:<!\[CDATA\[)?\s*attachment\s*(?:\]\]>)?\s*</wp:post_type>'
        if re.search(post_type_pattern, item_block, flags=re.IGNORECASE):
            attachment_items_blocks.append(item_block)
    
    # Get the date from the last attachment item
    if attachment_items_blocks:
        post_date_pattern = r'<wp:post_date\b[^>]*>\s*(?:<!\[CDATA\[)?\s*(.*?)\s*(?:\]\]>)?\s*</wp:post_date>'
        post_date_match = re.search(post_date_pattern, attachment_items_blocks[-1], flags=re.IGNORECASE)
        if post_date_match:
            post_date = post_date_match.group(1)
    
    return attachment_root_items, attachment_items, media_category_terms, post_date

def main():
    parser = argparse.ArgumentParser(
        description="Count <item> and <wp:category> tags in XML retrieved from URLs listed in a CSV. Also extracts the post date."
    )
    parser.add_argument("-i", "--input", default="exports/mediatecas.csv", help="Input CSV path")
    parser.add_argument("-o", "--output", default="exports/medias_xml_tag_counts.csv", help="Output CSV path")
    parser.add_argument("-c", "--column", default=None, help="URL column name (optional)")
    parser.add_argument("--nombre", type=str, default=None, help="Nombre column name (optional)")
    parser.add_argument("-d", "--xml-dir", dest="xml_dir", default=None, help="Directory containing XML files (optional; local mode)")
    parser.add_argument("-t", "--timeout", type=int, default=20, help="HTTP timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="HTTP retry attempts")
    parser.add_argument("--backoff", type=float, default=0.3, help="Backoff factor for retries")
    args = parser.parse_args()

    input_csv = args.input
    output_csv = args.output
    timeout = args.timeout
    retries = args.retries
    backoff = args.backoff
    nombre_arg = args.nombre
    xml_dir = args.xml_dir

    session = create_session_with_retries(retries=retries, backoff_factor=backoff)

    try:
        with open(input_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or []
            url_col = args.column or detect_url_column(header)
            nombre_col = nombre_arg or detect_nombre_column(header)
            if url_col not in header:
                print(f"Error: URL column '{url_col}' not found in input CSV header: {header}", file=sys.stderr)
                sys.exit(2)
            if nombre_col and nombre_col not in header:
                # If a nombre column was requested but not found, ignore it
                nombre_col = ""

            # Prepare to write output
        with open(input_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = ["numero", "nombre", "url", "attachment_root_items", "attachment_items", "media_category_terms", "post_date", "error"]

            with open(output_csv, "w", newline="", encoding="utf-8") as out_f:
                writer = csv.DictWriter(out_f, fieldnames=fieldnames)
                writer.writeheader()

                total = 0
                success = 0
                for line_num, row in enumerate(reader, start=2):
                    nombre_val = (row.get(nombre_col) or "") if nombre_col else ""
                    url = (row.get(url_col) or "").strip()
                    total += 1

                    # Print progress: line number and name
                    print(f"Processing line {line_num}: {nombre_val}")

                    if not url:
                        writer.writerow({
                            "numero": line_num,
                            "nombre": nombre_val,
                            "url": "",
                            "attachment_root_items": "",
                            "attachment_items": "",
                            "media_category_terms": "",
                            "error": "missing_url"
                        })
                        continue

                    attachment_root_items = 0
                    attachment_items = 0
                    media_category_terms = 0
                    post_date = ""
                    error = ""

                    try:
                        if xml_dir:
                            filename = extract_filename_from_url(url)
                            if not filename:
                                raise ValueError("Cannot derive filename from URL: " + url)
                            # Resolve to existing file in dir with robust handling
                            resolved = filename
                            candidate_path = os.path.join(xml_dir, resolved)
                            if not os.path.exists(candidate_path):
                                # Try with .xml extension
                                if not resolved.lower().endswith(".xml"):
                                    cand_ext = resolved + ".xml"
                                    if os.path.exists(os.path.join(xml_dir, cand_ext)):
                                        resolved = cand_ext
                                        candidate_path = os.path.join(xml_dir, resolved)
                                if not os.path.exists(candidate_path):
                                    found = None
                                    try:
                                        for f in os.listdir(xml_dir):
                                            if f.lower().startswith(filename.lower()):
                                                found = f
                                                break
                                    except FileNotFoundError:
                                        found = None
                                    if found:
                                        resolved = found
                                        candidate_path = os.path.join(xml_dir, resolved)
                                    else:
                                        raise FileNotFoundError(f"Local XML file not found for '{url}' in '{xml_dir}'")
                            print(f"Line {line_num}: nombre={nombre_val}, url={url}, filename={filename}, resolved={resolved} (local file)")
                            xml_text = read_xml_from_dir(resolved, xml_dir)
                        else:
                            xml_text = fetch_xml(url, timeout=timeout, session=session)
                        attachment_root_items, attachment_items, media_category_terms, post_date = count_tags(xml_text)
                        success += 1
                    except FileNotFoundError as e:
                        error = f"file_not_found:{str(e)}"
                    except Exception as e:
                        error = str(e)

                    writer.writerow({
                        "numero": line_num,
                        "nombre": nombre_val,
                        "url": url,
                        "attachment_root_items": attachment_root_items,
                        "attachment_items": attachment_items,
                        "media_category_terms": media_category_terms,
                        "post_date": post_date,
                        "error": error
                    })

        print(f"Processed {total} rows. Successful fetches: {success}. Output written to {output_csv}")
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting gracefully.", file=sys.stderr)
        sys.exit(130)
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_csv}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
