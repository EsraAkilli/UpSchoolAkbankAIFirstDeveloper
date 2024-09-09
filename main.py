import os
import streamlit as st
import ffmpeg
from openai import OpenAI
from dotenv import load_dotenv
from langdetect import detect
from PIL import Image

st.set_page_config(
    page_title="Video Translator App",
)

logo = Image.open("anagörsel.png")
st.image(logo, width=800)

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mp3'}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_video_to_audio(video_path, audio_path):
    stream = ffmpeg.input(video_path)
    stream = ffmpeg.output(stream, audio_path)
    ffmpeg.run(stream)

def transcribe_audio(audio_path):
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="srt"
        )
    return transcript

def translate_text(text, target_language):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": f"You are a translator. Translate the following SRT content to {target_language}. Maintain the SRT format including timestamps."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def detect_language(text):
    try:
        return detect(text)
    except:
        return "Unknown"

def main():
    st.title("Video Translation App")

    st.subheader("🎥 Upload Video File")
    uploaded_file = st.file_uploader("Select a video file:", type=ALLOWED_EXTENSIONS)

    if uploaded_file is not None:
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error(f"File size exceeds the {MAX_FILE_SIZE / (1024 * 1024):.2f} MB limit. Please upload a smaller file.")
            return

        st.subheader("Video Preview")
        st.video(uploaded_file)

        st.subheader("🌐 Language Selection")
        languages = st.multiselect(
            "Select target languages:",
            ["French", "German", "Spanish", "Italian", "Turkish", "Chinese", "English", "Arabic", "Portuguese", "Russian", "Japanese"]
        )

        if languages and st.button("🚀 Process Video"):
            progress_bar = st.progress(0)

            video_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            audio_path = os.path.join(OUTPUT_FOLDER, 'output.wav')
            with st.spinner("Converting video to audio..."):
                convert_video_to_audio(video_path, audio_path)
                progress_bar.progress(25)

            with st.spinner("Transcribing audio..."):
                transcript = transcribe_audio(audio_path)
                progress_bar.progress(50)

            st.success("Audio transcribed successfully!")

            source_language = detect_language(transcript[:1000])
            st.info(f"Detected source language: {source_language}")

            st.subheader("📝 Transcript")
            edited_transcript = st.text_area("Edit transcript if needed:", transcript, height=300)

            translations = {}
            total_languages = len(languages)
            for index, lang in enumerate(languages):
                with st.spinner(f"Translating to {lang}..."):
                    translations[lang] = translate_text(edited_transcript, lang)
                    progress = 50 + (50 * (index + 1) / total_languages)
                    progress_bar.progress(int(progress))

            st.success("Translation completed!")
            progress_bar.progress(100)

            st.subheader("🔄 Translated Subtitles")
            for lang, translation in translations.items():
                st.write(f"{lang}:")

                st.text_area(f"{lang} SRT Content", translation, height=300)

                file_path = os.path.join(OUTPUT_FOLDER, f'{lang}_translation.srt')
                with open(file_path, 'w') as f:
                    f.write(translation)

                with open(file_path, 'r') as f:
                    st.download_button(
                        label=f"Download {lang} SRT ⬇️",
                        data=translation,
                        file_name=f'{lang}_translation.srt',
                        mime='text/plain',
                        key=f'download_{lang}'
                    )

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    main()

st.sidebar.header("📋 Instructions")
st.sidebar.markdown("""
1. Upload a video file (mp4, avi, mov, or mp3 format).
2. Review the video preview to ensure you've uploaded the correct file.
3. Select target language(s) for translation.
4. Click 'Process Video' to transcribe and translate the audio.
5. Review the detected source language and edit the transcript if needed.
6. View the translated subtitles and download the SRT files.
""")