
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

def get_gemini_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None



from prism.core import (
    ollama_chat, extract_document_text, image_question,
    create_presentation, create_storyboard_video, generate_image_local,
    transcribe_audio_local, speak_text_local, ollama_status
)

st.set_page_config(page_title="Prism Multimodal AI Studio", page_icon="🔮", layout="wide")
st.title("🔮 Prism Multimodal AI Studio")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020, #20143b);
}
[data-testid="stSidebar"] {
    background-color: #111426;
}
h1 {
    color: #c4b5fd;
}
</style>
""", unsafe_allow_html=True)

st.caption("Local-first multimodal workspace • Ollama + open-source tools")
st.markdown("""
<div style="
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(120deg, #30205f, #172554);
    border: 1px solid #6551a8;
    margin: 20px 0;
">
    <h1 style="color:white;">Welcome to Prism ✨</h1>
    <p style="color:#e0e7ff;font-size:18px;">
        Your All-in-One Multimodal AI Workspace
    </p>
    <p style="color:#c4b5fd;">
        Chat • Documents • Images • Slides • Video
    </p>
</div>
""", unsafe_allow_html=True)

st.subheader("🚀 Explore Your AI Tools")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("💬 AI Chat\n\nAsk questions and explore ideas.")

with col2:
    st.info("📄 Documents\n\nUpload and summarize documents.")

with col3:
    st.info("🖼️ Image Understanding\n\nAnalyze uploaded images.")

col4, col5, col6 = st.columns(3)

with col4:
    st.info("🎨 Image Studio\n\nCreate images from text prompts.")

with col5:
    st.info("📊 Slides Studio\n\nCreate presentations.")

with col6:
    st.info("🎬 Video Studio\n\nBuild storyboard videos.")

with st.sidebar:
    st.title("✨ Prism AI Studio")
    st.caption("Your local multimodal AI workspace")

    st.divider()

    selected_page = st.radio(
        "Navigation",
        [
            "💬 Chat",
            "📄 Documents",
            "🖼️ Understand image",
            "🎙️ Voice",
            "🎨 Generate image",
            "📊 Slides",
            "🎬 Video",
            "??? History",
            "⚙️ Advanced Settings",
        ],
        label_visibility="collapsed",
        key="prism_navigation",
    )


pages = [
    "💬 Chat",
    "📄 Documents",
    "🖼️ Understand image",
    "🎙️ Voice",
    "🎨 Generate image",
    "📊 Slides",
    "🎬 Video",
]


if selected_page == "💬 Chat":
    st.subheader("💬 AI Chat Assistant")

    provider = st.selectbox(
        "AI Provider",
        ["Gemini API", "Local Ollama"],
        key="ai_provider",
    )

    if provider == "Gemini API":
        model = st.text_input(
            "Gemini model",
            value="gemini-3.8-flash",
            key="gemini_chat_model",
        )
    else:
        model = st.text_input(
            "Ollama model",
            value="qwen2.5:3b",
            key="chat_model",
        )

    from prism.history import save_item

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask Prism anything...")

    if prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt}
        )

        save_item(
            kind="Chat",
            title="Chat question",
            details=f"Provider: {provider}; Model: {model}",
            content=prompt,
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if provider == "Gemini API":
                        api_key = get_gemini_api_key()
                        if not api_key:
                            raise ValueError(
                                "GEMINI_API_KEY পাওয়া যায়নি। .env ফাইল পরীক্ষা করো।"
                            )

                        client = genai.Client(api_key=api_key)
                        response = client.models.generate_content(
                            model=model,
                            contents=prompt,
                        )
                        answer = response.text or "No text returned."
                    else:
                        answer = ollama_chat(model, prompt)
                except Exception as e:
                    answer = f"Error: {type(e).__name__}: {e}"

                st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )

        save_item(
            kind="Chat",
            title="Prism response",
            details=f"Provider: {provider}; Model: {model}",
            content=answer,
        )

    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.rerun()

elif selected_page == "📄 Documents":
    st.subheader("📄 Document Assistant")

    provider = st.selectbox(
        "AI Provider",
        ["Gemini API", "Local Ollama"],
        key="document_provider",
    )

    uploaded = st.file_uploader(
        "Upload PDF, DOCX, or TXT",
        type=["pdf", "docx", "txt"],
        key="doc",
    )

    if uploaded:
        try:
            content = extract_document_text(
                uploaded.name, uploaded.getvalue()
            )
            st.success(f"Extracted {len(content):,} characters.")

            with st.expander("Preview document"):
                st.text(content[:12000])

            q = st.text_area(
                "What would you like to know?",
                value="Summarize this document in Bengali bullet points.",
                key="doc_question",
            )

            if provider == "Gemini API":
                model = st.text_input(
                    "Gemini model",
                    value="gemini-3.8-flash",
                    key="document_gemini_model",
                )
            else:
                model = st.text_input(
                    "Ollama model",
                    value="qwen2.5:3b",
                    key="document_ollama_model",
                )

            if st.button("Analyze document", key="analyze_doc"):
                prompt = f"""
Answer based only on the document below.
If the answer is not in the document, say so.
Respond in Bengali unless requested otherwise.

DOCUMENT:
{content[:30000]}

QUESTION:
{q}
"""
                with st.spinner("Analyzing document..."):
                    try:
                        if provider == "Gemini API":
                            api_key = get_gemini_api_key()
                            if not api_key:
                                raise ValueError(
                                    "GEMINI_API_KEY পাওয়া যায়নি। .env পরীক্ষা করো।"
                                )
                            client = genai.Client(api_key=api_key)
                            response = client.models.generate_content(
                                model=model, contents=prompt
                            )
                            answer = response.text or "No text returned."
                        else:
                            answer = ollama_chat(model, prompt)

                        st.markdown("### Analysis")
                        st.markdown(answer)
                        from prism.history import save_item
                        save_item(
                            kind="Document",
                            title=uploaded.name,
                            details=f"Question: {q}\nProvider: {provider}; Model: {model}",
                            content=answer,
                        )
                    except Exception as e:
                        st.error(f"{type(e).__name__}: {e}")
        except Exception as e:
            st.error(f"Document processing failed: {e}")

elif selected_page == "🖼️ Understand image":
    st.subheader("🖼️ Image Understanding")
    img = st.file_uploader(
        "Upload an image",
        type=["png", "jpg", "jpeg", "webp"],
        key="image",
    )
    if img:
        st.image(img, use_container_width=True)
        question = st.text_input(
            "What should Prism look for?",
            value="Describe this image in detail.",
            key="image_q",
        )
        vision_model = st.text_input(
            "Vision model",
            value="qwen2.5vl:3b",
            key="vision_model",
        )
        if st.button("Analyze image"):
            with st.spinner("Analyzing image..."):
                try:
                    result = image_question(
                        vision_model, question, img.getvalue()
                    )
                    st.markdown(result)
                    from prism.history import save_item
                    save_item(
                        kind="Image Question",
                        title=img.name,
                        details=f"Question: {question}\nModel: {vision_model}",
                        content=result,
                    )
                except Exception as e:
                    st.error(str(e))


elif selected_page == "🎙️ Voice":
    st.subheader("🎙️ Voice Assistant")
    st.info("Record your voice or upload an audio file.")

    # Record directly from the browser microphone.
    recorded_audio = st.audio_input("Record your voice", key="voice_recording")

    uploaded_audio = st.file_uploader(
        "Or upload audio (WAV/MP3/M4A/OGG)",
        type=["wav", "mp3", "m4a", "ogg"],
        key="audio",
    )

    audio = recorded_audio if recorded_audio is not None else uploaded_audio

    whisper_model = st.selectbox(
        "Speech model",
        ["base", "small", "medium"],
        index=0,
    )

    if audio is not None:
        st.audio(audio)

        if st.button("Transcribe audio", key="transcribe_voice"):
            with st.spinner("Transcribing audio..."):
                try:
                    transcript = transcribe_audio_local(
                        audio.getvalue(),
                        getattr(audio, "name", "recording.wav"),
                        whisper_model,
                    )
                    st.session_state["voice_transcript"] = transcript
                    st.success("Transcription complete.")
                except Exception as e:
                    st.error(f"Transcription failed: {e}")

    transcript = st.text_area(
        "Transcript / text to answer",
        value=st.session_state.get("voice_transcript", ""),
        height=120,
        key="voice_transcript_editor",
    )

    if st.button("Ask Prism and speak", key="ask_prism_voice"):
        if transcript.strip():
            with st.spinner("Generating response..."):
                try:
                    answer = ollama_chat("qwen2.5:3b", transcript)
                    st.markdown("### Prism's response")
                    st.write(answer)

                    audio_path = speak_text_local(answer)
                    st.audio(audio_path)
                except Exception as e:
                    st.error(f"Voice response failed: {e}")
        else:
            st.warning("Please record audio or enter text first.")

elif selected_page == "🎨 Generate image":
    st.subheader("🎨 Image Studio")
    st.caption("Create an image from a text prompt.")

    image_prompt = st.text_area(
        "Describe your image",
        value="A peaceful futuristic library, cinematic lighting, detailed digital art",
    )

    if st.button("Generate image"):
        with st.spinner("Generating image..."):
            try:
                output = generate_image_local(image_prompt)
                image_bytes = Path(output).read_bytes()

                from prism.history import save_file, save_item

                saved_path = save_file(
                    "prism_generated.png",
                    image_bytes,
                    prefix="image",
                )

                save_item(
                    kind="Generated Image",
                    title="prism_generated.png",
                    details=f"Prompt: {image_prompt}",
                    content=image_prompt,
                    file_path=saved_path,
                )

                st.image(image_bytes, caption="Generated image")
                st.success("Image created and saved to History!")

                st.download_button(
                    "Download image",
                    data=image_bytes,
                    file_name="prism_generated.png",
                    mime="image/png",
                    key="download_prism_generated_image",
                )
            except Exception as e:
                st.error(str(e))
                st.caption("Check the image-generation dependencies in README.md.")

elif selected_page == "📊 Slides":
    st.subheader("📊 Presentation Studio")
    title = st.text_input(
        "Presentation title",
        value="Introduction to Multimodal AI",
    )
    topic = st.text_area(
        "Topic / source notes",
        value="Explain text, image, audio, and video understanding in AI.",
    )
    slide_count = st.slider("Number of slides", 3, 12, 6)

    if st.button("Create presentation"):
        with st.spinner("Creating slides..."):
            try:
                outline = ollama_chat(
                    "qwen2.5:3b",
                    f"Create exactly {slide_count} presentation slides about: "
                    f"{topic}. Return plain text with slides separated by ===. "
                    "Each slide needs a title and 3-5 concise bullet points.",
                )
                pptx_path = create_presentation(title, outline)

                from prism.history import save_file, save_item
                saved_path = save_file(
                    "prism_presentation.pptx",
                    Path(pptx_path).read_bytes(),
                    prefix="slides",
                )
                save_item(
                    kind="Slides",
                    title=title,
                    details=f"Slides: {slide_count}",
                    content=outline,
                    file_path=saved_path,
                )

                st.success("Presentation created and saved to History!")
                st.download_button(
                    "Download PowerPoint",
                    data=Path(pptx_path).read_bytes(),
                    file_name="prism_presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    key="download_prism_presentation",
                )
                with st.expander("Preview slide outline"):
                    st.text_area(
                        "Generated outline", outline, height=250
                    )
            except Exception as e:
                st.error(str(e))

elif selected_page == "🎬 Video":
    st.subheader("🎬 Video Studio")
    st.caption("Create a storyboard video from text scenes.")

    video_title = st.text_input(
        "Video title",
        value="What is Multimodal AI?",
        key="video_title",
    )
    video_script = st.text_area(
        "Scenes (one scene per paragraph)",
        value=(
            "Multimodal AI works with more than one type of data.\n\n"
            "It can understand text and images.\n\n"
            "It can also process audio and video.\n\n"
            "Prism brings these tools together in one workspace."
        ),
        key="video_script",
    )

    if st.button("Build video"):
        with st.spinner("Rendering video..."):
            try:
                path = create_storyboard_video(
                    video_title, video_script
                )

                with open(path, "rb") as f:
                    video_bytes = f.read()

                from prism.history import save_file, save_item

                saved_path = save_file(
                    "prism_storyboard.mp4",
                    video_bytes,
                    prefix="video",
                )

                save_item(
                    kind="Video",
                    title=video_title,
                    details="Storyboard video created successfully",
                    content=video_script,
                    file_path=saved_path,
                )

                st.video(video_bytes)
                st.success("Video created and saved to History!")

                st.download_button(
                    "Download MP4",
                    data=video_bytes,
                    file_name="prism_storyboard.mp4",
                    mime="video/mp4",
                    key="download_prism_storyboard_video",
                )
            except Exception as e:
                st.error(str(e))
                st.caption(
                    "Video rendering requires Pillow, imageio, "
                    "imageio-ffmpeg, and a working FFmpeg backend."
                )


elif selected_page == "??? History":
    st.header("??? History")
    st.caption("Saved Prism conversations, documents, images and other outputs.")

    try:
        from prism.history import list_items, delete_item

        kind = st.selectbox(
            "Filter history",
            ["All", "Chat", "Document", "Image Question",
             "Voice", "Generated Image", "Slides", "Video"]
        )

        items = list_items(kind)

        if not items:
            st.info("No saved history yet. New items will appear here after saving is connected.")
        else:
            for item in items:
                with st.expander(
                    f"{item['created_at']} ? {item['kind']}: {item['title']}"
                ):
                    if item.get("details"):
                        st.write(item["details"])
                    if item.get("content"):
                        st.text_area(
                            "Saved content",
                            item["content"],
                            height=180,
                            key=f"history_content_{item['id']}",
                        )
                    file_path = item.get("file_path", "")
                    if file_path and Path(file_path).is_file():
                        file = Path(file_path)
                        st.download_button(
                            "Download saved file",
                            data=file.read_bytes(),
                            file_name=file.name,
                            key=f"history_download_{item['id']}",
                        )
                    if st.button("Delete entry", key=f"history_delete_{item['id']}"):
                        delete_item(item["id"])
                        st.rerun()
    except Exception as e:
        st.error(f"Could not load history: {e}")

elif selected_page == "⚙️ Advanced Settings":
    st.header("⚙️ Advanced Settings")

    status = ollama_status()

    st.subheader("System status")
    if isinstance(status, str) and "connected" in status.lower():
        st.success("Local AI models connected")
    else:
        st.info(status)

    with st.expander("Advanced model details"):
        st.caption("Chat model: qwen2.5:3b")
        st.caption("Vision model: qwen2.5vl:3b")
        st.markdown("[Get Ollama](https://ollama.com)")

    st.subheader("🔒 Privacy")
    st.caption(
        "Local models process your files and prompts on this device. "
        "External AI services may receive data if enabled."
    )

