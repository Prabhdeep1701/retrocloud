from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

ROOT_DIRECTORY = "/Users/prabhdeepsingh/Desktop/retrocloud/shared" 

@router.get("/browse")
def browse(path: str = ""):
    abs_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, path))

    if not abs_path.startswith(ROOT_DIRECTORY):
        raise HTTPException(status_code=403, detail="Access denied.")

    if not os.path.exists(abs_path):
        raise HTTPException(status_code=404, detail="Path not found.")

    files = []
    for item in os.listdir(abs_path):
        item_path = os.path.join(abs_path, item)
        files.append({
            "name": item,
            "path": os.path.relpath(item_path, ROOT_DIRECTORY),
            "is_dir": os.path.isdir(item_path)
        })
    return {"current_path": path, "contents": files}

@router.get("/download")
def download(path: str):
    abs_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, path))

    if not abs_path.startswith(ROOT_DIRECTORY):
        raise HTTPException(status_code=403, detail="Access denied.")
    
    if not os.path.exists(abs_path) or os.path.isdir(abs_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    return FileResponse(abs_path, filename=os.path.basename(abs_path))

