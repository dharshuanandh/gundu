# Local Development Setup with VSCode

This guide will help you set up the Missing Person Finder project to run locally using VSCode.

## Prerequisites

- **Python 3.8+** installed on your machine
- **VSCode** with Python extension
- **Git** (to clone the repository)

## Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd missing-person-finder
   ```

2. **Run the setup script**:
   ```bash
   ./setup-local.sh
   ```

3. **Open in VSCode**:
   ```bash
   code missing-person-finder.code-workspace
   ```

### Option 2: Manual Setup

1. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Open in VSCode**:
   ```bash
   code .
   ```

## Running the Application

### Method 1: Using VSCode Debugger (Recommended)

1. **Open the debug panel** (Ctrl+Shift+D)
2. **Select "Run Missing Person Finder"** from the dropdown
3. **Press F5** or click the play button
4. **Open http://127.0.0.1:8000** in your browser

### Method 2: Using VSCode Tasks

1. **Open command palette** (Ctrl+Shift+P)
2. **Type "Tasks: Run Task"**
3. **Select "Run Server"**
4. **Open http://127.0.0.1:8000** in your browser

### Method 3: Using Terminal

1. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

2. **Run the server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

3. **Open http://127.0.0.1:8000** in your browser

## VSCode Features Configured

- **Automatic virtual environment detection**
- **Python linting with flake8**
- **Code formatting with black**
- **Debug configurations** for normal and debug modes
- **Task automation** for common operations
- **HTML syntax highlighting** for the frontend

## Available Tasks

- **Create Virtual Environment**: Sets up the Python virtual environment
- **Install Dependencies**: Installs required Python packages
- **Run Server**: Starts the FastAPI development server
- **Test Face Search**: Runs the test script

## Troubleshooting

### Python interpreter not found
1. Open command palette (Ctrl+Shift+P)
2. Type "Python: Select Interpreter"
3. Choose the interpreter from `.venv/bin/python`

### Port 8000 already in use
1. Change the port in `.vscode/launch.json` and `.vscode/tasks.json`
2. Or kill the process using port 8000:
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

### Dependencies installation failed
1. Ensure you have the latest pip:
   ```bash
   pip install --upgrade pip
   ```
2. Try installing dependencies one by one:
   ```bash
   pip install fastapi
   pip install uvicorn[standard]
   # ... etc
   ```

## Project Structure

```
missing-person-finder/
├── app/
│   ├── main.py          # FastAPI application
│   ├── face_search.py   # Face recognition logic
│   └── static/
│       └── index.html   # Speech Emotion Recognition interface
├── data/                # Stored images and encodings
├── .vscode/             # VSCode configuration
├── requirements.txt     # Python dependencies
├── missing-person-finder.code-workspace  # VSCode workspace file
└── setup-local.sh       # Automated setup script
```

## Features

- **Speech Emotion Recognition interface** with real-time audio processing
- **Face search functionality** (original feature)
- **REST API** for integration
- **Modern web UI** with responsive design
- **Live audio visualization** and emotion detection

Happy coding! 🚀
