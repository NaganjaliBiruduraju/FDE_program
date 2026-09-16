from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.pipeline.document_pipeline import DocumentPipeline


router = APIRouter()

pipeline = DocumentPipeline()


@router.post("/extract")
async def extract_document(
    file: UploadFile = File(...),
):
    """Extract structured information from an uploaded PDF."""

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
            query=(
                "What is the document title, authors, "
                "research topic, objective, dataset, "
                "methodology, algorithms, results, "
                "findings, and conclusions?"
            ),
            top_k=15,
        )

        return {
            "document": result["document"].model_dump(),
            "evaluation": result["evaluation"],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    finally:
        if file_path.exists():
            file_path.unlink()