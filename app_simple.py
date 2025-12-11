#!/usr/bin/env python
"""
Minimal Missing Person Finder - Simple HTTP Server (no uvicorn needed)
Run with: python app_simple.py
"""
import os
import sys
import json
import pickle
from typing import List, Dict, Any, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urljoin, urlparse
import io
import numpy as np
from PIL import Image
import cv2

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
ENC_PATH = os.path.join(DATA_DIR, "encodings.pkl")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Simple face search functions (from app/face_search.py)
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
    os.makedirs(folder, exist_ok=True)
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

# HTML Page
HTML_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Missing Person Finder</title>
    <style>
      body{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}
      .container{max-width:900px;margin:0 auto;background:white;padding:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
      h1{color:#333}
      .box{margin-bottom:30px;padding:15px;background:#f9f9f9;border-left:4px solid #007bff}
      h3{margin-top:0;color:#007bff}
      input[type="file"], input[type="number"], button{padding:8px 12px;margin:5px 5px 5px 0;border:1px solid #ddd;border-radius:4px;font-size:14px}
      button{background:#007bff;color:white;cursor:pointer;border:none}
      button:hover{background:#0056b3}
      #indexResult, #searchResult{margin-top:10px;padding:10px;background:#e8f4f8;border-radius:4px}
      .match{display:inline-block;margin:10px;text-align:center;background:#fff;padding:10px;border:1px solid #ddd;border-radius:4px}
      .match img{max-width:150px;max-height:150px;display:block;margin-bottom:10px;border-radius:4px}
      .match div{font-size:12px;color:#666}
    </style>
  </head>
  <body>
    <div class="container">
      <h1>🔍 Missing Person Finder</h1>
      <p>A college project to find similar faces in event images.</p>

      <div class="box">
        <h3>📤 Step 1: Index Images</h3>
        <p>Upload multiple event/crowd photos (JPG, PNG)</p>
        <input id="indexFiles" type="file" multiple accept="image/*" />
        <button id="indexBtn">Upload & Index</button>
        <div id="indexResult"></div>
      </div>

      <div class="box">
        <h3>🔎 Step 2: Search</h3>
        <p>Upload a missing-person photo to find similar faces</p>
        <input id="probeFile" type="file" accept="image/*" />
        <label>Results to show: <input id="topk" type="number" value="5" min="1" max="20" style="width:60px"/></label>
        <button id="searchBtn">Search</button>
        <div id="searchResult"></div>
      </div>

      <div class="box">
        <h3>ℹ️ Info</h3>
        <div id="status"></div>
      </div>
    </div>

    <script>
      // Load status on page load
      fetch('/api/status').then(r => r.json()).then(d => {
        document.getElementById('status').innerHTML = `Faces indexed: <b>${d.indexed_faces}</b>`;
      }).catch(e => {
        document.getElementById('status').innerHTML = 'Status: offline';
      });

      document.getElementById('indexBtn').onclick = async () => {
        const files = document.getElementById('indexFiles').files;
        if (!files.length) return alert('Choose image files to index');
        document.getElementById('indexResult').innerText = 'Uploading...';
        const fd = new FormData();
        for (let f of files) fd.append('files', f);
        try {
          const res = await fetch('/api/index', {method:'POST', body:fd});
          const j = await res.json();
          document.getElementById('indexResult').innerHTML = `✅ Saved <b>${j.saved_files}</b> files, indexed <b>${j.faces_indexed}</b> faces`;
          fetch('/api/status').then(r => r.json()).then(d => {
            document.getElementById('status').innerHTML = `Faces indexed: <b>${d.indexed_faces}</b>`;
          });
        } catch(e) {
          document.getElementById('indexResult').innerHTML = '❌ Error: ' + e.message;
        }
      };

      document.getElementById('searchBtn').onclick = async () => {
        const f = document.getElementById('probeFile').files[0];
        if (!f) return alert('Select a probe image');
        const topk = document.getElementById('topk').value || 5;
        document.getElementById('searchResult').innerHTML = 'Searching...';
        const fd = new FormData();
        fd.append('file', f);
        fd.append('top_k', topk);
        try {
          const res = await fetch('/api/search', {method:'POST', body:fd});
          if (!res.ok) {
            const t = await res.json();
            return document.getElementById('searchResult').innerHTML = '❌ ' + (t.detail || 'Unknown error');
          }
          const j = await res.json();
          const el = document.getElementById('searchResult');
          el.innerHTML = '';
          if (!j.results.length) {
            el.innerText = 'No matches found';
            return;
          }
          el.innerHTML = '<h4>Top ' + j.results.length + ' matches:</h4>';
          for (let r of j.results) {
            const d = document.createElement('div');
            d.className = 'match';
            const img = document.createElement('img');
            img.src = r.url;
            img.onerror = () => img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="150" height="150"%3E%3Crect fill="%23ccc" width="150" height="150"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="14" fill="%23999"%3EImage not found%3C/text%3E%3C/svg%3E';
            const p = document.createElement('div');
            p.innerHTML = `Distance: <b>${r.distance.toFixed(4)}</b><br/><small>${r.file}</small>`;
            d.appendChild(img);
            d.appendChild(p);
            el.appendChild(d);
          }
        } catch(e) {
          document.getElementById('searchResult').innerHTML = '❌ ' + e.message;
        }
      };
    </script>
  </body>
</html>
"""

# HTTP Request Handler
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path.startswith("/images/"):
            fname = self.path.split("/")[-1]
            fpath = os.path.join(IMAGES_DIR, fname)
            if os.path.exists(fpath):
                try:
                    with open(fpath, "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-Type", "image/jpeg")
                        self.end_headers()
                        self.wfile.write(f.read())
                except:
                    self.send_response(500)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == "/api/status":
            encs = load_encodings(ENC_PATH)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"indexed_faces": len(encs)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if self.path == "/api/index":
            try:
                # Parse multipart form data (simple version)
                import re
                files_data = []
                # Extract filename and binary data from multipart
                parts = body.split(b"--")
                for part in parts:
                    if b"filename=" in part:
                        try:
                            fn_match = re.search(b'filename="([^"]+)"', part)
                            if fn_match:
                                fname = fn_match.group(1).decode()
                                # Find the binary data after \r\n\r\n
                                split_idx = part.find(b"\r\n\r\n")
                                if split_idx > 0:
                                    data = part[split_idx+4:-2]  # Remove \r\n at end
                                    if data:
                                        fpath = os.path.join(IMAGES_DIR, os.path.basename(fname))
                                        with open(fpath, "wb") as f:
                                            f.write(data)
                                        files_data.append(fname)
                        except:
                            pass

                saved = len(files_data)
                added = index_folder(IMAGES_DIR, ENC_PATH)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"saved_files": saved, "faces_indexed": added}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        elif self.path == "/api/search":
            try:
                # Extract file from multipart
                import re
                file_data = None
                top_k = 5

                parts = body.split(b"--")
                for part in parts:
                    if b'name="file"' in part and b"Content-Disposition" in part:
                        split_idx = part.find(b"\r\n\r\n")
                        if split_idx > 0:
                            file_data = part[split_idx+4:-2]
                    elif b'name="top_k"' in part:
                        split_idx = part.find(b"\r\n\r\n")
                        if split_idx > 0:
                            try:
                                top_k = int(part[split_idx+4:-2].decode().strip())
                            except:
                                pass

                if not file_data:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"detail": "No file provided"}).encode())
                    return

                probe = encode_image_bytes(file_data)
                if probe is None:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"detail": "No face found in probe image"}).encode())
                    return

                encs = load_encodings(ENC_PATH)
                results = find_matches(probe, encs, top_k=top_k)
                for r in results:
                    r["url"] = f"/images/{os.path.basename(r['file'])}"

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"results": results}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), RequestHandler)
    print("🚀 Missing Person Finder running at http://127.0.0.1:8000")
    print("   - Index event images at /")
    print("   - Search for missing person face")
    print("   - Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Server stopped.")
