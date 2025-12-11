import os
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil

from . import face_search

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
ENC_PATH = os.path.join(DATA_DIR, "encodings.pkl")

os.makedirs(IMAGES_DIR, exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


@app.get("/", response_class=HTMLResponse)
async def home():
    with open(os.path.join(BASE_DIR, "static", "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/api/index")
async def index_images(files: List[UploadFile] = File(...)):
    saved = 0
    for up in files:
        fname = os.path.basename(up.filename)
        dest = os.path.join(IMAGES_DIR, fname)
        with open(dest, "wb") as f:
            shutil.copyfileobj(up.file, f)
        saved += 1
    added = face_search.index_folder(IMAGES_DIR, ENC_PATH)
    return {"saved_files": saved, "faces_indexed": added}


@app.post("/api/search")
async def search_image(file: UploadFile = File(...), top_k: int = Form(5)):
    data = await file.read()
    probe = face_search.encode_image_bytes(data)
    if probe is None:
        raise HTTPException(status_code=400, detail="No face found in probe image")
    encs = face_search.load_encodings(ENC_PATH)
    results = face_search.find_matches(probe, encs, top_k=top_k)
    # convert relative paths used in encodings to image URLs for frontend
    for r in results:
        r["url"] = f"/images/{os.path.basename(r['file'])}"
    return JSONResponse({"results": results})


@app.get("/api/status")
async def status():
    encs = face_search.load_encodings(ENC_PATH)
    return {"indexed_faces": len(encs)}
