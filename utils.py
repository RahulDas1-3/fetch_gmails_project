# utils.py


import base64
from typing import Dict, List




def get_header(headers: List[Dict[str, str]], name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""




def decode_b64(data_b64: str) -> str:
    try:
        return base64.urlsafe_b64decode(data_b64.encode("utf-8")).decode("utf-8", errors="replace")
    except Exception:
        return ""




def extract_plain_text_from_payload(payload: Dict) -> str:
    """
    Walk the MIME tree and try to extract a human-readable plain text.
    Prefers 'text/plain'; falls back to 'text/html' (stripped).
    """
    if not payload:
        return ""


    mime_type = payload.get("mimeType", "")
    body = payload.get("body", {})
    data = body.get("data")


    # Single-part
    if data and (mime_type.startswith("text/plain") or mime_type.startswith("text/html")):
        text = decode_b64(data)
        if mime_type.startswith("text/html"):
            import re
            text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
            text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
            text = re.sub(r"<[^>]+>", "", text)
        return text


    # Multipart
    parts = payload.get("parts", [])
    best_html = ""
    for p in parts or []:
        t = p.get("mimeType", "")
        b = p.get("body", {}).get("data")


        if p.get("parts"):  # nested multipart
            sub = extract_plain_text_from_payload(p)
            if sub:
                return sub


        if b and t.startswith("text/plain"):
            return decode_b64(b)


        if b and t.startswith("text/html"):
            html_text = decode_b64(b)
            import re
            html_text = re.sub(r"<br\s*/?>", "\n", html_text, flags=re.I)
            html_text = re.sub(r"</p\s*>", "\n\n", html_text, flags=re.I)
            html_text = re.sub(r"<[^>]+>", "", html_text)
            if not best_html:
                best_html = html_text


    return best_html
