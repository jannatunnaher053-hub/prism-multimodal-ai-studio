# Prism Multimodal AI Studio (Local-first)

This is a runnable starter application for Windows. It provides:
- Local text chat through Ollama
- PDF, DOCX and TXT text extraction + local-model Q&A
- Image understanding through an Ollama vision model
- Local audio transcription through faster-whisper
- Local text-to-speech through pyttsx3
- PowerPoint slide generation using python-pptx and a local LLM
- A simple MP4 storyboard builder from text scenes
- Optional Stable Diffusion image generation (heavy; install separately)

Important limits:
- The video tab renders text-based scene cards into an MP4. It is not a full text-to-video generative model.
- Scanned PDFs may need OCR; this starter extracts embedded PDF text only.
- Local models need adequate memory/storage. Image generation can be slow or fail on CPU-only PCs.
- Model weights are downloaded to your computer when you pull/load them; the first run needs internet.
- No cloud API is used by default.

## 1. Install Ollama
Install Ollama for Windows from https://ollama.com and open it.

In PowerShell, pull the text model:
```powershell
ollama pull qwen2.5:3b
```

For image understanding, pull a vision model:
```powershell
ollama pull qwen2.5vl:3b
```
If your PC has limited RAM, start with smaller models supported by Ollama.

## 2. Open the project folder
Extract the ZIP into:
`C:\Users\UESR\Downloads\prism`

Make sure `app.py`, `requirements.txt`, and the `prism` package folder are directly inside `prism`, not nested inside another folder.

## 3. Create / activate virtual environment
```powershell
cd C:\Users\UESR\Downloads\prism
.\penv\Scripts\Activate.ps1
```
If `penv` does not exist, create it:
```powershell
python -m venv penv
.\penv\Scripts\Activate.ps1
```
If PowerShell blocks activation in this terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\penv\Scripts\Activate.ps1
```

## 4. Install packages
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
If a dependency fails on your Python version, use Python 3.11 or 3.12 for best compatibility, then recreate the environment.

## 5. Run Prism
```powershell
python -m streamlit run app.py
```
A browser tab should open at a local address, usually `http://localhost:8501`.

## Optional: enable local image generation
This is a large install and may require many GB of downloads. First check your hardware and available disk space. Then, inside the activated environment:
```powershell
python -m pip install -r requirements-image-generation.txt
```
The first image generation downloads model weights. A compatible NVIDIA GPU is recommended; CPU mode may be extremely slow.

## Troubleshooting
- Ollama not detected: open the Ollama app, then run `ollama list`.
- Model missing: `ollama pull qwen2.5:3b` or `ollama pull qwen2.5vl:3b`.
- Port busy: `python -m streamlit run app.py --server.port 8502`.
- Voice transcription first run downloads Whisper model files.
- If audio format fails, convert the recording to WAV and retry.
- The voice output language depends on voices installed on Windows; Bengali voice quality/availability varies.
