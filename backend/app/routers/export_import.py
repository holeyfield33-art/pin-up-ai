"""Export / Import router per api-contract.md.

Rule: export must NEVER be blocked by license status.
"""

import json
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_token
from app.schemas import ExportRequest, ImportResponse
from app.services import export_service, import_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["export_import"], dependencies=[Depends(verify_token)])


@router.post("/export")
def export_data(body: ExportRequest, db: Session = Depends(get_db)):
    """Export snippets. Always allowed regardless of license status."""
    fmt = body.format.lower()
    try:
        if fmt == "json":
            data = export_service.export_json(db, scope=body.scope, ids=body.ids or None)
            return JSONResponse(content=data)
        elif fmt == "markdown":
            path = export_service.export_markdown_zip(db, scope=body.scope, ids=body.ids or None)
            return FileResponse(
                path, media_type="application/zip",
                filename="pinup_export.zip",
            )
        elif fmt == "bundle":
            path = export_service.export_bundle(db, scope=body.scope, ids=body.ids or None)
            return FileResponse(
                path, media_type="application/zip",
                filename="pinup_bundle.zip",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail={"code": "VALIDATION_ERROR", "message": f"Unknown format: {fmt}"},
            )
    except Exception as e:
        logger.error("Export error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "EXPORT_ERROR", "message": str(e)},
        )


@router.post("/import", response_model=ImportResponse)
async def import_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import from JSON bundle."""
    try:
        content = await file.read()
        data = json.loads(content)
        result = import_service.import_bundle(db, data)
        return result
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail={"code": "IMPORT_ERROR", "message": "Invalid JSON file"},
        )
    except Exception as e:
        logger.error("Import error: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"code": "IMPORT_ERROR", "message": str(e)},
        )
