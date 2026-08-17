import base64
import json
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pdf2image import convert_from_path
from app.core.config import settings

GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
OCR_PROMPT = ("Transcribe this document image exactly. Preserve spelling, punctuation, "
              "and visible layout as closely as possible. Do not correct, infer, "
              "summarize, or invent text. Mark unreadable text as [unclear]. "
              "Return a semantic HTML fragment in content, not Markdown and not a "
              "full HTML document. Use only p, br, strong, em, h1, h2, h3, ul, ol, "
              "li, table, thead, tbody, tr, th, and td. Use strong for visibly bold "
              "headings or labels, em for visibly italic text, and tables when the "
              "image contains tabular structure. Preserve the original reading order "
              "and wording exactly; use formatting only to represent what is visible.")


def _detect_text(image_bytes: bytes, media_type: str) -> str:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    payload = {"contents": [{"parts": [
        {"inline_data": {"mime_type": media_type, "data": base64.b64encode(image_bytes).decode("ascii")}},
        {"text": OCR_PROMPT},
    ]}], "generationConfig": {
        "responseMimeType": "application/json",
        "responseSchema": {"type": "OBJECT", "properties": {"content": {"type": "STRING"}}, "required": ["content"]},
        "temperature": 0,
    }}
    url = GEMINI_URL.format(model=GEMINI_MODEL, key=settings.gemini_api_key)
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")

    try:
        with urlopen(request, timeout=60) as response:
            result = json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini request failed ({error.code}): {detail}") from error

    if result.get("error"):
        raise RuntimeError(result["error"].get("message", "Gemini request failed"))
    try:
        response_text = result["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(response_text).get("content", "").strip()
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
        raise RuntimeError("Gemini returned an invalid OCR response") from error

def extract_text_from_file(file_path: str) -> dict:
    results = {"status": "success", "total_pages": 0, "pages": []}
    try:
        path = Path(file_path)
        if path.suffix.lower() == ".pdf":
            images = convert_from_path(file_path)
            results["total_pages"] = len(images)

            for page_number, image in enumerate(images, start=1):
                image_buffer = BytesIO()
                image.save(image_buffer, format="PNG")
                text = _detect_text(image_buffer.getvalue(), "image/png")
                results["pages"].append({
                    "page_number": page_number,
                    "content": text,
                })
        elif path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            media_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            text = _detect_text(path.read_bytes(), media_type)
            results["total_pages"] = 1
            results["pages"].append({"page_number": 1, "content": text})
        else:
            raise ValueError("Unsupported OCR file type")

    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
            "total_pages": 0,
            "pages": [],
        }

    return results
