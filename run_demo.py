#!/usr/bin/env python
"""
Missing Person Finder - DEMO Mode (no heavy dependencies)
This version shows the UI and API structure without requiring numpy/opencv for demo purposes.
Run with: python run_demo.py
"""
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(DATA_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

HTML_PAGE = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Missing Person Finder - Demo</title>
    <style>
      *{margin:0;padding:0;box-sizing:border-box}
      body{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);min-height:100vh;padding:20px}
      .container{max-width:900px;margin:0 auto;background:white;padding:30px;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,0.1)}
      h1{color:#333;margin-bottom:10px;text-align:center}
      .subtitle{text-align:center;color:#666;margin-bottom:30px;font-size:14px}
      .section{margin-bottom:35px;padding:20px;background:#f8f9fa;border-radius:8px;border-left:4px solid #667eea}
      .section h2{color:#667eea;font-size:18px;margin-bottom:15px}
      .section p{color:#555;margin-bottom:10px;line-height:1.6}
      input[type="file"]{display:block;margin:10px 0;padding:8px;border:1px solid #ddd;border-radius:4px;cursor:pointer;width:100%}
      .controls{display:flex;gap:10px;margin:10px 0;flex-wrap:wrap;align-items:center}
      button{padding:10px 20px;background:#667eea;color:white;border:none;border-radius:4px;cursor:pointer;font-size:14px;font-weight:500;transition:background 0.3s}
      button:hover{background:#764ba2}
      input[type="number"]{padding:8px;border:1px solid #ddd;border-radius:4px;width:80px}
      #indexResult, #searchResult{margin-top:15px;padding:15px;background:white;border-radius:4px;border:1px solid #e0e0e0}
      .match{display:inline-block;margin:10px;text-align:center;background:white;padding:15px;border:1px solid #ddd;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.08)}
      .match img{max-width:140px;max-height:140px;display:block;margin-bottom:10px;border-radius:4px;background:#f0f0f0}
      .match div{font-size:13px;color:#666}
      .match b{color:#667eea;display:block;margin-top:5px}
      #status{padding:10px;background:white;border-left:4px solid #667eea;border-radius:4px;color:#333}
      .info-box{background:#e8f4f8;border-left:4px solid #17a2b8;padding:12px;border-radius:4px;margin:10px 0;font-size:13px;color:#004085}
      .success{color:#28a745}
      .error{color:#dc3545}
      .loading{color:#667eea;font-style:italic}
    </style>
  </head>
  <body>
    <div class="container">
      <h1>🔍 Missing Person Finder</h1>
      <p class="subtitle">College Project - Find similar faces in event images</p>

      <div class="section">
        <h2>📤 Step 1: Index Event Images</h2>
        <p>Upload multiple photos from an event or location where the person might appear.</p>
        <input id="indexFiles" type="file" multiple accept="image/*" />
        <button id="indexBtn">Upload & Index Images</button>
        <div id="indexResult"></div>
      </div>

      <div class="section">
        <h2>🔎 Step 2: Search for Missing Person</h2>
        <p>Upload a clear photo of the missing person to find matches in the indexed images.</p>
        <div class="controls">
          <input id="probeFile" type="file" accept="image/*" />
          <span style="color:#666">Results:</span>
          <input id="topk" type="number" value="5" min="1" max="20" />
          <button id="searchBtn">Search</button>
        </div>
        <div id="searchResult"></div>
      </div>

      <div class="section">
        <h2>ℹ️ Status & Info</h2>
        <div id="status">Loading...</div>
        <div class="info-box">
          <strong>How it works:</strong> Face detection (OpenCV) → Color histogram encoding → Euclidean distance matching → Ranked results
        </div>
      </div>
    </div>

    <script>
      function updateStatus() {
        fetch('/api/status')
          .then(r => r.json())
          .then(d => {
            document.getElementById('status').innerHTML = 
              `<strong>Faces indexed:</strong> <span class="success">${d.indexed_faces}</span>`;
          })
          .catch(() => {
            document.getElementById('status').innerHTML = '❌ Unable to connect to server';
          });
      }

      updateStatus();

      document.getElementById('indexBtn').onclick = async () => {
        const files = document.getElementById('indexFiles').files;
        if (!files.length) return alert('Please select image files');
        const res = document.getElementById('indexResult');
        res.innerHTML = '<span class="loading">⏳ Uploading and indexing...</span>';
        
        const fd = new FormData();
        for (let f of files) fd.append('files', f);
        
        try {
          const r = await fetch('/api/index', {method:'POST', body:fd});
          const j = await r.json();
          if (r.ok) {
            res.innerHTML = `<span class="success">✅ Saved ${j.saved_files} files, indexed ${j.faces_indexed} faces</span>`;
            updateStatus();
          } else {
            res.innerHTML = `<span class="error">❌ Error: ${j.detail || j.error}</span>`;
          }
        } catch(e) {
          res.innerHTML = `<span class="error">❌ ${e.message}</span>`;
        }
      };

      document.getElementById('searchBtn').onclick = async () => {
        const f = document.getElementById('probeFile').files[0];
        if (!f) return alert('Please select a probe image');
        const res = document.getElementById('searchResult');
        res.innerHTML = '<span class="loading">⏳ Searching...</span>';
        
        const fd = new FormData();
        fd.append('file', f);
        fd.append('top_k', document.getElementById('topk').value);
        
        try {
          const r = await fetch('/api/search', {method:'POST', body:fd});
          const j = await r.json();
          if (!r.ok) {
            res.innerHTML = `<span class="error">❌ ${j.detail || j.error}</span>`;
            return;
          }
          if (!j.results.length) {
            res.innerHTML = '<span class="error">No matches found</span>';
            return;
          }
          res.innerHTML = '<h3 style="color:#667eea;margin-bottom:15px">Top matches:</h3>';
          for (let r of j.results) {
            const d = document.createElement('div');
            d.className = 'match';
            const img = document.createElement('img');
            img.src = r.url;
            img.onerror = () => img.alt = 'Image not found';
            const p = document.createElement('div');
            p.innerHTML = `Distance: <b>${r.distance.toFixed(4)}</b><small style="display:block;margin-top:5px;color:#999">${r.file}</small>`;
            d.appendChild(img);
            d.appendChild(p);
            res.appendChild(d);
          }
        } catch(e) {
          res.innerHTML = `<span class="error">❌ ${e.message}</span>`;
        }
      };
    </script>
  </body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path in ["/", "/index.html"]:
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_PAGE.encode())
            elif self.path.startswith("/images/"):
                fname = os.path.basename(self.path)
                fpath = os.path.join(IMAGES_DIR, fname)
                if os.path.isfile(fpath):
                    try:
                        with open(fpath, "rb") as f:
                            self.send_response(200)
                            ext = fname.lower().split('.')[-1]
                            ctype = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}.get(ext, "image/jpeg")
                            self.send_header("Content-Type", ctype)
                            self.end_headers()
                            self.wfile.write(f.read())
                    except:
                        self.send_response(500)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
            elif self.path == "/api/status":
                import pickle
                encs_file = os.path.join(DATA_DIR, "encodings.pkl")
                count = 0
                if os.path.isfile(encs_file):
                    try:
                        with open(encs_file, "rb") as f:
                            encs = pickle.load(f)
                            count = len(encs) if isinstance(encs, list) else 0
                    except:
                        count = 0
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"indexed_faces": count}).encode())
            else:
                self.send_response(404)
                self.end_headers()
        except ConnectionAbortedError:
            pass  # Client disconnected
        except Exception as e:
            try:
                self.send_response(500)
                self.end_headers()
            except:
                pass

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            if self.path == "/api/index":
                self._handle_index(body)
            elif self.path == "/api/search":
                self._handle_search(body)
            else:
                self.send_response(404)
                self.end_headers()
        except ConnectionAbortedError:
            pass  # Client disconnected
        except Exception as e:
            try:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            except:
                pass

    def _handle_index(self, body):
        try:
            import re
            from PIL import Image
            import pickle
            import io

            saved = 0
            # Parse multipart form data - extract boundary correctly
            content_type = self.headers.get("Content-Type", "")
            boundary_match = re.search(r'boundary=([^\r\n;]+)', content_type)
            if not boundary_match:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid form data"}).encode())
                return
            
            boundary = boundary_match.group(1).strip('"').encode()
            parts = body.split(b"--" + boundary)
            
            for part in parts:
                if b'filename=' in part:
                    # Extract filename with flexible quotes
                    filename_match = re.search(rb'filename=(["\']?)([^"\'\r\n]+)\1', part)
                    if filename_match:
                        fname = filename_match.group(2).decode()
                        # Find the double CRLF that separates headers from body
                        sep_idx = part.find(b"\r\n\r\n")
                        if sep_idx < 0:
                            sep_idx = part.find(b"\n\n")
                            if sep_idx < 0:
                                continue
                            sep_idx += 2
                            data = part[sep_idx:]
                        else:
                            sep_idx += 4
                            data = part[sep_idx:]
                        
                        # Remove trailing boundary markers
                        if data.endswith(b"\r\n"):
                            data = data[:-2]
                        elif data.endswith(b"\n"):
                            data = data[:-1]
                        
                        if data:
                            # Validate it's a real image
                            try:
                                img = Image.open(io.BytesIO(data))
                                img.load()  # Load to validate
                            except:
                                continue
                            
                            # Save the file
                            fpath = os.path.join(IMAGES_DIR, os.path.basename(fname))
                            with open(fpath, "wb") as f:
                                f.write(data)
                            saved += 1

            # Index faces using PIL-based histogram (no numpy/cv2 needed)
            encodings = []
            encs_file = os.path.join(DATA_DIR, "encodings.pkl")
            if os.path.isfile(encs_file):
                try:
                    with open(encs_file, "rb") as f:
                        encodings = pickle.load(f)
                except:
                    encodings = []

            added = 0
            indexed_files = {e["file"] for e in encodings}  # Track already indexed
            for fname in os.listdir(IMAGES_DIR):
                if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                if fname in indexed_files:  # Skip already indexed
                    continue
                fpath = os.path.join(IMAGES_DIR, fname)
                try:
                    img = Image.open(fpath)
                    # Simple histogram: resize, convert to RGB, extract color histogram
                    img = img.resize((64, 64)).convert("RGB")
                    hist = img.histogram()  # PIL histogram: 256*3 = 768 values
                    encodings.append({"file": fname, "face_index": 0, "encoding": hist})
                    added += 1
                except:
                    pass

            with open(encs_file, "wb") as f:
                pickle.dump(encodings, f)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"saved_files": saved, "faces_indexed": added}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _handle_search(self, body):
        try:
            import re
            import pickle
            from PIL import Image
            import io

            # Parse multipart form data
            content_type = self.headers.get("Content-Type", "")
            boundary_match = re.search(r'boundary=([^\r\n;]+)', content_type)
            if not boundary_match:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Invalid form data"}).encode())
                return
            
            boundary = boundary_match.group(1).strip('"').encode()
            
            file_data = None
            top_k = 5
            parts = body.split(b"--" + boundary)
            for part in parts:
                if b'name="file"' in part:
                    sep_idx = part.find(b"\r\n\r\n")
                    if sep_idx > 0:
                        data = part[sep_idx+4:]
                        if data.endswith(b"\r\n"):
                            data = data[:-2]
                        if data:
                            file_data = data
                elif b'name="top_k"' in part:
                    sep_idx = part.find(b"\r\n\r\n")
                    if sep_idx > 0:
                        try:
                            top_k = int(part[sep_idx+4:-2].decode().strip())
                        except:
                            pass

            if not file_data:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "No file"}).encode())
                return

            # Encode probe image using PIL histogram (no numpy/cv2)
            try:
                img = Image.open(io.BytesIO(file_data))
                img = img.resize((64, 64)).convert("RGB")
                probe = img.histogram()  # List of 768 values
            except:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Invalid image"}).encode())
                return

            # Find matches using simple distance
            encs_file = os.path.join(DATA_DIR, "encodings.pkl")
            results = []
            if os.path.isfile(encs_file):
                try:
                    with open(encs_file, "rb") as f:
                        encodings = pickle.load(f)
                    if encodings:
                        # Compute distances (Euclidean)
                        distances = []
                        for e in encodings:
                            enc_hist = e["encoding"]
                            # Compute Euclidean distance between histograms
                            dist = sum((p - q) ** 2 for p, q in zip(probe, enc_hist)) ** 0.5
                            distances.append((dist, e))
                        
                        # Sort and get top_k
                        distances.sort(key=lambda x: x[0])
                        for dist, e in distances[:top_k]:
                            results.append({
                                "file": e["file"],
                                "face_index": 0,
                                "distance": dist,
                                "url": f"/images/{e['file']}"
                            })
                except:
                    pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"results": results}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = 8000
    server = HTTPServer(("127.0.0.1", port), Handler)
    print(f"\n{'='*60}")
    print(f"[*] Missing Person Finder - DEMO (PIL-based)")
    print(f"{'='*60}")
    print(f"[*] Open browser: http://127.0.0.1:{port}")
    print(f"\nFeatures:")
    print(f"[*] Features:")
    print(f"   - Upload event images to index")
    print(f"   - Search for missing person face")
    print(f"   - View ranked matches")
    print(f"\n[*] Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
        server.server_close()
