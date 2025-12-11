# Missing Person Finder (College Project)

Simple Face-similarity webapp to index event images and search for a missing person by face.

Features
- Upload many event images to index faces and compute embeddings.
- Upload a probe (missing person) image to find visually similar faces.
- Simple web UI and REST API (FastAPI).

Requirements
- Python 3.8+
- dlib is required by ace_recognition. On Windows installing dlib can be tricky; see https://github.com/davisking/dlib for platform instructions.

Quick setup (Windows / macOS / Linux)

1) Create and activate a virtualenv

`ash
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # macOS / Linux
`

2) Install dependencies

`ash
pip install -r requirements.txt
`

3) Run the app

`ash
uvicorn app.main:app --reload
`

4) Open the UI

Visit http://127.0.0.1:8000 in your browser. Use "Index images" to upload event photos (multiple). Then use "Search" to upload the missing-person image.

Notes
- Encodings are saved under data/encodings.pkl and images under data/images.
- If ace_recognition is difficult to install, consider using deepface as an alternative (update code accordingly).

License
- For college project use only.
