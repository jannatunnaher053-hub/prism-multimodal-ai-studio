import streamlit as st
from pathlib import Path
from prism.core import (
    ollama_chat, extract_document_text, image_question,
    create_presentation, create_storyboard_video, generate_image_local,
    transcribe_audio_local, speak_text_local, ollama_status
)

st.set_page_config(page_title="Prism Multimodal AI Studio", page_icon="🔮", layout="wide")
st.title("🔮 Prism Multimodal AI Studio")
st.caption("Local-first multimodal workspace • Ollama + open-source tools")

with st.sidebar:
    st.header("Local model status")
    status = ollama_status()
    st.write(status)
    st.markdown("**Suggested chat model:** `qwen2.5:3b`")
    st.markdown("**Suggested vision model:** `qwen2.5vl:3b`")
    st.markdown("Install Ollama from https://ollama.com, then run the model commands in README.md.")
    st.divider()
    st.subheader("Privacy")
    st.write("Files and prompts are processed locally by this app and local models, unless you separately configure another service.")

tabs = st.tabs(["💬 Chat", "📄 Documents", "🖼️ Understand image", "🎙️ Voice", "🖼️ Generate image", "📊 Slides", "🎬 Video"])

with tabs[0]:
    st.subheader("Local AI chat")
    model = st.text_input("Ollama model", value="qwen2.5:3b", key="chat_model")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    prompt = st.chat_input("Ask Prism anything…")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking locally…"):
                answer = ollama_chat(model, prompt)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

with tabs[1]:
    st.subheader("Ask questions about documents")
    uploaded = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"], key="doc")
    if uploaded:
        try:
            content = extract_document_text(uploaded.name, uploaded.getvalue())
            st.success(f"Extracted {len(content):,} characters.")
            with st.expander("Preview extracted text"):
                st.text(content[:12000])
            q = st.text_input("Question about this document", key="doc_question", value="Summarize this document in bullet points.")
            doc_model = st.text_input("Ollama model", value="qwen2.5:3b", key="doc_model")
            if st.button("Analyze document", key="analyze_doc"):
                with st.spinner("Analyzing with local model…"):
                    answer = ollama_chat(doc_model, f"Answer based only on the document below. If the answer is not in the document, say so.\n\nDOCUMENT:\n{content[:24000]}\n\nQUESTION: {q}")
                st.markdown(answer)
        except Exception as e:
            st.error(str(e))

with tabs[2]:
    st.subheader("Image understanding")
    img = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"], key="image")
    if img:
        st.image(img, use_container_width=True)
        question = st.text_input("What should Prism look for?", value="Describe this image in detail.", key="image_q")
        vision_model = st.text_input("Vision model", value="qwen2.5vl:3b", key="vision_model")
        if st.button("Analyze image"):
            with st.spinner("Analyzing image locally…"):
                result = image_question(vision_model, question, img.getvalue())
            st.markdown(result)

with tabs[3]:
    st.subheader("Voice input and voice response")
    st.info("For the first local version, upload an audio recording to transcribe it. Microphone recording support depends on your browser and installed audio components.")
    audio = st.file_uploader("Upload audio (WAV/MP3/M4A)", type=["wav", "mp3", "m4a", "ogg"], key="audio")
    whisper_model = st.selectbox("Local speech model", ["base", "small", "medium"], index=0)
    if audio and st.button("Transcribe audio locally"):
        with st.spinner("Loading local Whisper model (first run downloads model files)…"):
            try:
                transcript = transcribe_audio_local(audio.getvalue(), audio.name, whisper_model)
                st.session_state["voice_transcript"] = transcript
            except Exception as e:
                st.error(str(e))
    transcript = st.text_area("Transcript / text to answer", value=st.session_state.get("voice_transcript", ""), height=120)
    if st.button("Ask Prism and speak the answer"):
        with st.spinner("Generating response…"):
            answer = ollama_chat("qwen2.5:3b", transcript)
        st.markdown(answer)
        try:
            audio_path = speak_text_local(answer)
            st.audio(audio_path)
        except Exception as e:
            st.warning(f"Text response is ready, but local voice output failed: {e}")

with tabs[4]:
    st.subheader("Local image generation")
    st.warning("Image generation needs a compatible computer and large model downloads. This optional feature uses Diffusers and Stable Diffusion; it may not run well without a suitable GPU.")
    image_prompt = st.text_area("Describe the image", value="A peaceful futuristic library, cinematic lighting, detailed digital art")
    if st.button("Generate image locally"):
        with st.spinner("Loading Stable Diffusion pipeline (first run may take a long time)…"):
            try:
                output = generate_image_local(image_prompt)
                st.image(output, caption="Generated locally")
                with open(output, "rb") as f:
                    st.download_button("Download image", f, file_name="prism_generated.png", mime="image/png")
            except Exception as e:
                st.error(str(e))
                st.caption("See README.md for optional image-generation installation notes.")

with tabs[5]:
    st.subheader("Create a PowerPoint presentation")
    title = st.text_input("Presentation title", value="Introduction to Multimodal AI")
    topic = st.text_area("Topic / source notes", value="Explain text, image, audio, and video understanding in AI.")
    slide_count = st.slider("Number of slides", 3, 12, 6)
    if st.button("Create PPTX"):
        with st.spinner("Drafting slide content with local model…"):
            outline = ollama_chat("qwen2.5:3b", f"Create exactly {slide_count} presentation slides about: {topic}. Return plain text in this format, each slide separated by a line containing ===. Each slide: title on first line, then 3-5 concise bullet points beginning with '-'. No intro or conclusion outside the slides.")
            try:
                pptx_path = create_presentation(title, outline)
                st.success("Presentation created.")
                with open(pptx_path, "rb") as f:
                    st.download_button("Download PowerPoint", f, file_name="prism_presentation.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
                st.text_area("Generated outline", outline, height=250)
            except Exception as e:
                st.error(str(e))

with tabs[6]:
    st.subheader("Local video builder")
    st.write("This first version creates a narrated-style storyboard video from text cards. It is not a full text-to-video diffusion model; a true local text-to-video model requires substantially more GPU memory and setup.")
    video_title = st.text_input("Video title", value="What is Multimodal AI?", key="video_title")
    video_script = st.text_area("Scenes (one scene per paragraph)", value="Multimodal AI works with more than one type of data.\n\nIt can understand text and images.\n\nIt can also process audio and video.\n\nPrism brings these tools together in one workspace.", key="video_script")
    if st.button("Build MP4 from scenes"):
        with st.spinner("Rendering video locally…"):
            try:
                path = create_storyboard_video(video_title, video_script)
                with open(path, "rb") as f:
                    st.download_button("Download MP4", f, file_name="prism_storyboard.mp4", mime="video/mp4")
            except Exception as e:
                st.error(str(e))
                st.caption("Video rendering requires Pillow, imageio, imageio-ffmpeg, and a working FFmpeg backend.")
