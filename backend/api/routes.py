from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.pipeline.document_pipeline import DocumentPipeline


router = APIRouter()

pipeline = DocumentPipeline()


@router.post("/extract")
async def extract_document(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    """Process an uploaded PDF according to the user's prompt."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    if not prompt.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty",
        )

    upload_directory = Path("documents/uploads")
    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = upload_directory / file.filename

    try:
        content = await file.read()
        file_path.write_bytes(content)

        result = pipeline.process(
            pdf_path=file_path,
            user_prompt=prompt,
            top_k=15,
        )

        return {
            "document": result["document"].model_dump(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    finally:
        if file_path.exists():
            file_path.unlink()