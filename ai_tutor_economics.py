import os
import json
import asyncio
import tempfile
import random
import re

import streamlit as st
from docx import Document
import pygame
import edge_tts
from googletrans import Translator
from gtts import gTTS

# ===============================
# 🚀 App Config
# ===============================
st.set_page_config(page_title="📘 AI Economics Reader", layout="centered")
st.title("📘 AI Economics Tutor with Voice, Dictionary & Translation")
st.markdown("""
    <style>
        /* App-wide font and layout tweaks */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f8f9fa;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        /* Button color override */
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)
# ===============================
# 👤 Personal & Project Info
# ===============================
with st.container():
    st.markdown("""
        <div style="padding: 1rem; border: 2px solid #4CAF50; border-radius: 10px; background-color: #f0fdf4;">
            <h3 style="margin-bottom: 0.2em;">👨‍🎓 <strong>Muhajir Abdulmumin</strong></h3>
            <p style="margin: 0.3em 0;">📚 <strong>Track:</strong> Data Science and Machine Learning</p>
            <p style="margin: 0.3em 0;">🏫 <strong>3MTT DeepTech ID:</strong> FE/23/87937833</p>
            <p style="margin: 0.3em 0;">✉️ <strong>Email:</strong> <a href="mailto:muhajirabdumuminnn@gmail.com">muhajirabdumuminnn@gmail.com</a></p>
        </div>
    """, unsafe_allow_html=True)

# ===============================
# 🔧 Initialize Utilities
# ===============================
translator = Translator()
pygame.mixer.init()

# ===============================
# 📄 Document Handling
# ===============================
def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# ===============================
# 🌍 Translation
# ===============================
def translate_text(text, language):
    lang_map = {
        "🇬🇧 English": "en",
        "🇸🇦 Arabic": "ar"
    }
    if language not in lang_map:
        return text
    return translator.translate(text, dest=lang_map[language]).text

# ===============================
# 🧠 Voice Selection
# ===============================
def get_edge_voice(language, gender):
    voices = {
        "🇬🇧 English": {
            "Male": "en-GB-RyanNeural",
            "Female": "en-GB-SoniaNeural"
        },
        "🇳🇬 Nigerian English": {
            "Male": "en-NG-AbeoNeural",
            "Female": "en-NG-EzinneNeural"
        },
        "🇸🇦 Arabic": {
            "Male": "ar-EG-ShakirNeural",
            "Female": "ar-EG-SalmaNeural"
        }
    }
    return voices.get(language, {}).get(gender, "en-GB-RyanNeural")

# ===============================
# 🗣️ gTTS Fallback (Offline)
# ===============================
def gtts_fallback(text, lang_code="en", slow=False):
    tts = gTTS(text=text, lang=lang_code, slow=slow)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tts.save(tmpfile.name)
        pygame.mixer.init()
        pygame.mixer.music.load(tmpfile.name)
        pygame.mixer.music.play()

# ===============================
# 🔊 Audio Generator
# ===============================
def convert_and_play_audio(text, language="🇬🇧 English", gender="Male", engine="edge-tts"):
    unsupported_languages = ["🇳🇬 Hausa", "🧪 Yoruba", "🧪 Igbo"]
    if language in unsupported_languages:
        st.warning(f"⚠️ {language} voice synthesis is coming soon.")
        return

    voice = get_edge_voice(language, gender)
    rate = "-25%" if slow_voice else "+0%"  # Corrected: Add '+' for normal

    with st.spinner("🌀 Converting to speech..."):
        async def _speak():
            try:
                if engine == "gTTS":
                    gtts_fallback(text, lang_code="en", slow=slow_voice)
                    return

                communicate = edge_tts.Communicate(text, voice, rate=rate)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    output_path = f.name

                await communicate.save(output_path)

                pygame.mixer.init()
                pygame.mixer.music.load(output_path)
                pygame.mixer.music.play()

            except edge_tts.exceptions.NoAudioReceived:
                st.error("❌ Failed to generate audio. Try another voice.")

        asyncio.run(_speak())

# ===============================
# ⏯️ Audio Controls
# ===============================
def pause_audio():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()

def resume_audio():
    pygame.mixer.music.unpause()

def stop_audio():
    pygame.mixer.music.stop()

# ===============================
# 📲 UI Controls
# ===============================
uploaded_file = st.file_uploader("📂 Upload a lesson note (.docx)", type=["docx"])

st.sidebar.header("🎙️ Voice & Language Settings")

language = st.sidebar.selectbox(
    "🌐 Select Language",
    ["🇬🇧 English", "🇳🇬 Nigerian English", "🇳🇬 Hausa", "🧪 Yoruba", "🧪 Igbo"]
)

gender = st.sidebar.radio("🧑‍🎤 Select Voice Gender", ["Male", "Female"])
engine_choice = st.sidebar.radio("🛠️ Speech Engine", ["edge-tts", "gTTS"])

st.sidebar.subheader("🗣️ Voice Speed")
voice_speed = st.sidebar.radio("📢 Select Speed", ["Normal", "Slow"])
slow_voice = voice_speed == "Slow"

st.caption(f"🎧 Using {'slow' if slow_voice else 'normal'} voice speed")

st.sidebar.subheader("🧠 Smart Features")
eli5_mode = st.sidebar.checkbox("🧸 Simplify Explanation (ELI5 Mode)")

# ===============================
# 🧾 Main Logic
# ===============================
if uploaded_file is not None:
    with st.spinner("📄 Reading your document..."):
        original_text = extract_text_from_docx(uploaded_file)

    if not original_text.strip():
        st.error("❌ The uploaded document is empty or unreadable.")
    else:
        unsupported_languages = ["🇳🇬 Hausa", "🧪 Yoruba", "🧪 Igbo"]
        st.subheader("📄 Lesson Content")

        if language in unsupported_languages:
            st.write(original_text)
            st.warning(f"⚠️ {language} translation and voice are not available yet. Coming soon!")
        else:
            translated = translate_text(original_text, language)
            st.write(translated)

            if st.button("🔊 Read Aloud"):
                convert_and_play_audio(translated, language, gender, engine=engine_choice)

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("⏸ Pause"):
                    pause_audio()
            with col2:
                if st.button("▶️ Resume"):
                    resume_audio()
            with col3:
                if st.button("⏹ Stop"):
                    stop_audio()

def generate_quiz_questions(text, num_questions=3):
    sentences = [s.strip() for s in re.split(r'[.?!]', text) if len(s.strip().split()) > 5]
    random.shuffle(sentences)
    questions = []

    for sentence in sentences[:num_questions]:
        words = sentence.split()
        if len(words) < 6:
            continue
        answer_index = random.randint(1, len(words) - 2)
        answer = words[answer_index]
        words[answer_index] = "_____"
        question_text = " ".join(words)
        questions.append((question_text, answer))
    
    return questions

# 📘 Quiz Generator
st.subheader("🧪 Quiz Generator")

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
    st.session_state.quiz_total = 0

if st.button("🎲 Generate Quiz"):
    st.session_state.quiz_questions = generate_quiz_questions(original_text)

if "quiz_questions" in st.session_state:
    for idx, (q_text, correct_answer) in enumerate(st.session_state.quiz_questions):
        st.markdown(f"**Q{idx+1}:** {q_text}")
        user_input = st.text_input(f"Your answer for Q{idx+1}", key=f"quiz_{idx}")
        if user_input:
            if user_input.strip().lower() == correct_answer.lower():
                st.success("✅ Correct!")
                st.session_state.quiz_score += 1
            else:
                st.error(f"❌ Incorrect. Correct answer: **{correct_answer}**")
            st.session_state.quiz_total += 1

if st.session_state.quiz_total > 0:
    st.markdown(f"**📊 Score:** {st.session_state.quiz_score}/{st.session_state.quiz_total}")

# ===============================
# 📘 Economics Dictionary
# ===============================
@st.cache_data
def load_economics_dictionary():
    with open("economics_terms.json", "r") as f:
        return json.load(f)

econ_dict = load_economics_dictionary()

st.header("📚 Economics Dictionary")

terms_list = sorted(list(econ_dict.keys()))
search_term = st.selectbox("🔍 Search for a term:", [""] + [term.title() for term in terms_list])

if search_term:
    term = search_term.lower()
   
    if term in econ_dict:
        definition = econ_dict[term]["definition"]
        example = econ_dict[term].get("example", "")

        st.success(f"**{search_term.title()}**")
    
    if eli5_mode:
        simplified = " ".join(definition.split()[:15]) + "..." if len(definition.split()) > 15 else definition
        st.markdown(f"👶 **Simple Explanation**: {simplified}")
    else:
        st.markdown(f"📖 **Definition**: {definition}")
        
    if example:
        st.markdown(f"💡 **Example**: _{example}_")


        if st.button("🔊 Read Term Aloud", key=f"read_{term}"):
            convert_and_play_audio(f"{search_term}. {definition}. {example}", language, gender, engine_choice)

        if "favorites" not in st.session_state:
            st.session_state.favorites = []
        if "history" not in st.session_state:
            st.session_state.history = []

        if term not in st.session_state.history:
            st.session_state.history.append(term)

        if st.button("⭐ Add to Favorites", key=f"fav_{term}"):
            if term not in st.session_state.favorites:
                st.session_state.favorites.append(term)
                st.success("Added to favorites!")
            else:
                st.warning("Already in favorites.")
    else:
        st.error("❌ Term not found. Please try another or contribute to the dictionary.")

# ===============================
# 💬 Concept Explainer (Ask Me Anything)
# ===============================
st.header("💬 Ask Me Anything (Economics Assistant)")

user_question = st.text_input("❓ Ask a question about economics:")

if user_question:
    matched_answers = []
    user_question_lower = user_question.lower()

    for term, data in econ_dict.items():
        definition = data.get("definition", "")
        example = data.get("example", "")
        if term in user_question_lower or any(word in definition.lower() for word in user_question_lower.split()):
            matched_answers.append((term, definition, example))

    if matched_answers:
        for term, definition, example in matched_answers:
            st.markdown(f"### 🔍 {term.title()}")
            st.markdown(f"📖 **Definition**: {definition}")
            if example:
                st.markdown(f"💡 **Example**: _{example}_")
    else:
        st.warning("🤖 I couldn't find a match. Try asking in simpler terms or search the dictionary.")

# 🎯 Track learning history
if "viewed_terms" not in st.session_state:
    st.session_state.viewed_terms = set()

if search_term:
    term = search_term.lower()
    if term in econ_dict:
        st.session_state.viewed_terms.add(term)

# 📊 Track quiz scores (already added before)

# 📚 Smart Recommendations
st.header("📈 Your Learning Progress")

viewed = list(st.session_state.viewed_terms)
if viewed:
    st.markdown(f"✅ You've viewed **{len(viewed)} terms** so far.")
    if len(viewed) < 5:
        st.info("📌 Keep learning! View at least 5 terms to unlock personalized revision tips.")
    else:
        unseen_terms = [t for t in econ_dict if t not in viewed]
        st.markdown("📖 **Recommended terms for review:**")
        for rec_term in unseen_terms[:3]:
            st.markdown(f"- {rec_term.title()}")
else:
    st.warning("🚨 You haven't viewed any terms yet. Start learning from the dictionary above.")

# ===============================
# 📢 Footer
# ===============================
st.markdown("""---""")
st.markdown("""
    <div style='text-align: center; padding-top: 1rem;'>
        <p>🚀 <strong>3MTT Capstone Project</strong> | Made with 💡 by <strong>Muhajir Abdulmumin</strong></p>
        <p style='font-size: 0.85em;'>Contact: <a href='mailto:muhajirabdumuminnn@gmail.com'>muhajirabdumuminnn@gmail.com</a></p>
    </div>
""", unsafe_allow_html=True)
