import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
from PIL import Image
import cv2
import io


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def load_encodings(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        return pickle.load(f)


def save_encodings(encodings: List[Dict[str, Any]], path: str):
    with open(path, "wb") as f:
        pickle.dump(encodings, f)


def image_bytes_to_array(file_bytes: bytes):
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def _extract_face_encodings(image_cv) -> List[np.ndarray]:
    encodings = []
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = cascade.detectMultiScale(gray, 1.1, 4)
    
    for (x, y, w, h) in faces:
        face_img = image_cv[y:y+h, x:x+w]
        if face_img.size == 0:
            continue
        hist = cv2.calcHist([face_img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        encodings.append(hist)
    
    return encodings


def index_folder(folder: str, encodings_path: str) -> int:
    ensure_dir(folder)
    encodings = load_encodings(encodings_path)
    added = 0
    
    for root, _, files in os.walk(folder):
        for fname in files:
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            fpath = os.path.join(root, fname)
            try:
                img = cv2.imread(fpath)
                if img is None:
                    continue
                face_encs = _extract_face_encodings(img)
                for i, enc in enumerate(face_encs):
                    item = {"file": os.path.relpath(fpath), "face_index": i, "encoding": enc}
                    encodings.append(item)
                    added += 1
            except Exception:
                continue
    
    save_encodings(encodings, encodings_path)
    return added


def encode_image_bytes(file_bytes: bytes) -> Optional[np.ndarray]:
    try:
        arr = image_bytes_to_array(file_bytes)
        embeds = _extract_face_encodings(arr)
        if len(embeds) == 0:
            return None
        return embeds[0]
    except Exception:
        return None


def find_matches(encoding: np.ndarray, encodings: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    if len(encodings) == 0:
        return []
    all_encs = np.vstack([np.array(e["encoding"]) for e in encodings])
    diffs = all_encs - encoding
    dists = np.linalg.norm(diffs, axis=1)
    idx = np.argsort(dists)[:top_k]
    results = []
    for i in idx:
        e = encodings[int(i)]
        results.append({"file": e["file"], "face_index": e.get("face_index", 0), "distance": float(dists[int(i)])})
    return results
