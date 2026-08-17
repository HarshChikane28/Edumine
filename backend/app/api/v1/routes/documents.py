import html
from pathlib import Path

import bleach
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import get_db, require_permission
from app.models import Document, User
from app.services.ocr import extract_text_from_file
from app.services.storage import save_file
from io import BytesIO

from fastapi.responses import HTMLResponse, StreamingResponse
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

router = APIRouter()


@router.get("")
async def documents(
    _: User = Depends(require_permission("manage_documents")),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    rows = (await db.scalars(select(Document).order_by(Document.upload_date.desc()))).all()
    return [
        {
            "id": str(row.id),
            "filename": row.filename,
            "path": row.file_path,
            "category": row.category,
            "status": row.status.value if hasattr(row.status, "value") else row.status,
            "upload_date": row.upload_date.isoformat() if row.upload_date else None,
            "extracted_data": row.extracted_data,
        }
        for row in rows
    ]

@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    category: str = Form(...),
    _: User = Depends(require_permission("manage_documents")),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if file.content_type not in {"application/pdf", "image/png", "image/jpeg", "image/jpg"}:
        raise HTTPException(status_code=400, detail="Only PDFs and images are supported.")

    category = category.strip()
    if not category:
        raise HTTPException(status_code=400, detail="Document category is required.")

    relative_path = await save_file(file)

    # OCR needs the actual filesystem path, not the relative DB path.
    full_path = Path(settings.storage_dir) / relative_path

    extracted_data = extract_text_from_file(str(full_path))

    # Save document metadata + OCR result.
    new_doc = Document(
        filename=file.filename or "Untitled Document",
        file_path=relative_path,
        category=category,
        extracted_data=extracted_data,
        status=(
            "completed"
            if extracted_data.get("status") == "success"
            else "failed"
        ),
    )

    db.add(new_doc)

    await db.commit()
    await db.refresh(new_doc)

    return {
        "id": str(new_doc.id),
        "filename": new_doc.filename,
        "path": new_doc.file_path,
        "category": new_doc.category,
        "status": (
            new_doc.status.value
            if hasattr(new_doc.status, "value")
            else new_doc.status
        ),
        "pages_processed": extracted_data.get(
            "total_pages",
            0,
        ),
        "extracted_data": extracted_data,
    }


@router.get("/{document_id}/download-pdf")
async def download_digitized_document(
    document_id: str,
    _: User = Depends(require_permission("manage_documents")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id
        )
    )

    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    extracted_data = document.extracted_data or {}

    if extracted_data.get("status") != "success":
        raise HTTPException(
            status_code=400,
            detail="This document does not have successfully extracted OCR data.",
        )

    output = BytesIO()

    pdf = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title=f"{document.filename} - Digitized",
        author="Edumin",
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    body_style = styles["BodyText"]

    story = []

    # Header
    story.append(
        Paragraph(
            "EDUMIN",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Digitized Document",
            styles["Heading2"],
        )
    )

    story.append(Spacer(1, 8 * mm))

    # Metadata
    story.append(
        Paragraph(
            f"<b>Document:</b> {document.filename}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Category:</b> {document.category}",
            body_style,
        )
    )

    story.append(
        Paragraph(
            f"<b>Document ID:</b> {document.id}",
            body_style,
        )
    )

    if document.upload_date:
        story.append(
            Paragraph(
                f"<b>Uploaded:</b> "
                f"{document.upload_date.strftime('%d %B %Y, %H:%M')}",
                body_style,
            )
        )

    story.append(Spacer(1, 10 * mm))

    story.append(
        Paragraph(
            "Extracted Content",
            heading_style,
        )
    )

    story.append(Spacer(1, 4 * mm))

    # OCR pages
    pages = extracted_data.get("pages", [])

    for index, page in enumerate(pages):
        page_number = page.get(
            "page_number",
            index + 1,
        )

        content = page.get(
            "content",
            "",
        )

        if len(pages) > 1:
            story.append(
                Paragraph(
                    f"Page {page_number}",
                    styles["Heading3"],
                )
            )

        # Preserve OCR line breaks.
        paragraphs = content.split("\n")

        for paragraph in paragraphs:
            if paragraph.strip():
                safe_text = (
                    paragraph
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )

                story.append(
                    Paragraph(
                        safe_text,
                        body_style,
                    )
                )

                story.append(
                    Spacer(1, 2 * mm)
                )

        if index < len(pages) - 1:
            story.append(PageBreak())

    story.append(Spacer(1, 15 * mm))

    story.append(
        Paragraph(
            "Digitized by Edumin",
            styles["Normal"],
        )
    )

    pdf.build(story)

    output.seek(0)

    # Remove original extension.
    original_name = document.filename or "document"

    if "." in original_name:
        base_name = original_name.rsplit(
            ".",
            1,
        )[0]
    else:
        base_name = original_name

    download_name = (
        f"{base_name}-digitized.pdf"
    )

    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{download_name}"'
            )
        },
    )


@router.get("/{document_id}/download")
async def download_digitized_document_html(
    document_id: str,
    _: User = Depends(require_permission("manage_documents")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    extracted_data = document.extracted_data or {}
    if extracted_data.get("status") != "success":
        raise HTTPException(
            status_code=400,
            detail="This document does not have successfully extracted OCR data.",
        )

    pages_html = []
    pages = extracted_data.get("pages", [])
    for index, page in enumerate(pages):
        page_number = page.get("page_number", index + 1)
        content = bleach.clean(
            page.get("content", ""),
            tags=["p", "br", "strong", "em", "h1", "h2", "h3", "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td"],
            attributes={},
            strip=True,
        )
        heading = f"<h2>Page {page_number}</h2>" if len(pages) > 1 else ""
        pages_html.append(f'<section class="ocr-page">{heading}<div class="ocr-content">{content}</div></section>')

    title = html.escape(document.filename or "Digitized Document")
    category = html.escape(document.category or "")
    body = "".join(pages_html) or '<p class="empty">No text was extracted.</p>'
    content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - Digitized</title>
  <style>
    body {{ margin: 0; background: #f5f2f7; color: #211d24; font: 16px/1.6 Arial, sans-serif; }}
    main {{ max-width: 900px; margin: 32px auto; padding: 40px; background: white; box-shadow: 0 2px 12px #0001; }}
    h1 {{ margin: 0 0 6px; color: #4f378a; }}
    .meta {{ color: #625b68; margin-bottom: 32px; }}
    .ocr-page {{ border-top: 1px solid #ddd6e2; padding-top: 24px; margin-top: 24px; page-break-after: always; }}
    .ocr-page:last-child {{ page-break-after: auto; }}
    h2 {{ font-size: 18px; color: #4f378a; }}
    .ocr-content {{ overflow-wrap: anywhere; font: 15px/1.65 Arial, sans-serif; }}
    .ocr-content p {{ margin: 0 0 12px; }}
    .ocr-content h1, .ocr-content h2, .ocr-content h3 {{ color: #332456; margin: 18px 0 10px; }}
    .ocr-content table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
    .ocr-content th, .ocr-content td {{ border: 1px solid #cfc7d6; padding: 8px 10px; text-align: left; vertical-align: top; }}
    .ocr-content th {{ background: #eee8f5; font-weight: 700; }}
    .ocr-content ul, .ocr-content ol {{ margin: 8px 0 14px 24px; }}
    .empty {{ color: #625b68; }}
  </style>
</head>
<body><main>
  <h1>Digitized Document</h1>
  <div class="meta"><strong>Document:</strong> {title}<br><strong>Category:</strong> {category}</div>
  {body}
</main></body>
</html>"""

    base_name = (document.filename or "document").rsplit(".", 1)[0]
    return HTMLResponse(
        content=content,
        headers={"Content-Disposition": f'attachment; filename="{base_name}-digitized.html"'},
    )
