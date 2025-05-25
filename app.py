# app.py

import streamlit as st
import sounddevice as sd
import wavio
import time
import random
import whisper
import Levenshtein

# -------------------------
# 🌍 언어 선택 (토글)
# -------------------------
language = st.selectbox("🌐 언어 선택", ["English", "French", "German", "Japanese(beta)"])
language_codes = {
    "English": "en",
    "Korean": "ko",
    "Spanish": "es",
    "French": "fr",
    "German": "de"
}

# -------------------------
# 🗂 예문 리스트 (언어별)
# -------------------------
example_sentences = {
    "English": [
        "I thought the theater was farther than it actually is.",
        "Would you rather read a book or watch a movie tonight?",
        "She rarely arrives early, but today she came before everyone else.",
        "There’s a difference between thinking and overthinking everything.",
        "Can you bring the red umbrella from the living room?",
        "This is the third time they’ve thoroughly reviewed the report.",
        "He visited a rural village where rivers run between rocky hills.",
        "Did you really believe that he would be there on Thursday?",
        "I’ve never heard her pronounce the letter R so clearly before.",
        "The weather in northern regions is rather unpredictable in April.",
        "He can’t distinguish between ‘beach’ and ‘bitch’ when speaking fast.",
        "They brought vegetables, bread, and bottles of water to the picnic.",
        "I don't think I can finish this before the deadline tomorrow.",
        "She asked whether they wanted to join them for dinner downtown.",
        "Though it was raining heavily, they still went for a run together.",
        "You should have told me that before the teacher noticed.",
        "It’s surprisingly difficult to say ‘red lorry, yellow lorry’ quickly.",
        "How many voices did the voice actor actually use in that scene?",
        "The baby grabbed the rubber rabbit and threw it across the room.",
        "They thought those theories were thoroughly discredited years ago."
    ],
    "French": [
        "Quand il pleut le matin, je préfère rester à la maison avec un bon livre.",
        "Elle m’a dit qu’elle viendrait si elle terminait son travail à temps.",
        "Nous avons acheté du pain, du fromage et une bouteille de vin rouge.",
        "Ilest important de boire beaucoup d’eau, surtout quand il fait chaud.",
        "J’adore écouter de la musique pendant que je cuisine le dîner.",
        "Ils sont allés au marché parce qu’ils voulaient acheter des fruits frais.",
        "Ma sœur travaille dans une école où elle enseigne le français aux enfants.",
        "Même s’il est tard, je vais regarder un épisode de ma série préférée.",
        "Après le déjeuner, nous avons fait une promenade dans le parc.",
        "Tu peux m’appeler si tu as besoin de parler à quelqu’un ce soir.",
        "Je n’ai pas vu mon cousin depuis qu’il est parti vivre en Belgique.",
        "Le train était en retard à cause de la neige sur les rails.",
        "Elle ne mange pas de viande, mais elle adore les légumes grillés.",
        "Avant de sortir, n’oublie pas de prendre ton parapluie.",
        "Ils ont décidé de déménager pour être plus proches de leur famille.",
        "Je ne comprends pas pourquoi il ne veut pas venir avec nous.",
        "Mon père prépare souvent des crêpes le dimanche matin.",
        "Chaque fois que je vais à la mer, je ramène du sable dans mes chaussures.",
        "Il faut que tu finisses tes devoirs avant de regarder la télé.",
        "Bien qu’il fasse froid, les enfants jouent dehors avec enthousiasme."
    ],
    "German": [
        "Ich trinke morgens immer eine Tasse Kaffee mit Milch.",
        "Wenn es regnet, bleibe ich lieber den ganzen Tag zu Hause.",
        "Könnten Sie mir bitte sagen, wie spät es ist?",
        "Am Wochenende fahren wir oft mit dem Fahrrad in den Park.",
        "Er hat gestern vergessen, seine Hausaufgaben zu machen.",
        "Sie liest gerne Bücher, besonders Krimis und Romane.",
        "Nach dem Essen spülen wir gemeinsam das Geschirr.",
        "Der Zug hatte Verspätung wegen des starken Schneefalls.",
        "Ich muss jeden Morgen um sieben Uhr aufstehen.",
        "Meine Schwester studiert Biologie an der Universität.",
        "Im Sommer gehen wir manchmal im See schwimmen.",
        "Ich habe keine Lust, heute Abend auszugehen.",
        "Kannst du bitte das Fenster schließen? Es ist kalt.",
        "Sie hat mir gestern eine Nachricht auf WhatsApp geschickt.",
        "Wir essen normalerweise gegen acht Uhr zu Abend.",
        "Ich freue mich darauf, dich nächste Woche wiederzusehen.",
        "Der Lehrer erklärt die Grammatik sehr verständlich.",
        "Ich habe letzte Woche ein interessantes Museum besucht.",
        "Obwohl er müde war, hat er das ganze Buch gelesen.",
        "Ich versuche, jeden Tag mindestens 30 Minuten zu lesen."
    ],
    "Japanese(beta)": [
        "今日は学校の友だちと映画を見ました。",
        "母とスーパーに行って、りんごを買いました。",
        "私は朝ごはんのあとで本を読みます。",
        "兄は先週の土曜日に山へ行きました。",
        "この川の水はとてもきれいですね。",
        "私は毎日六時におきて、水を飲みます。",
        "友だちと一緒に公園でサッカーをしました。",
        "図書館で小さい本を三さつ読みました。",
        "日曜日に父と母とドライブに行きました。",
        "昨日の夜、家でカレーをつくりました。",
        "今日はいい天気だから、外で遊びたいです。",
        "家の近くに新しいパンやがあります。",
        "お昼ごはんの前に宿題をぜんぶやりました。",
        "この本の名前を先生に聞きました。",
        "魚が好きですが、肉はあまり食べません。",
        "弟は八時に学校へ行きました。",
        "あの山の上に小さいお寺があります。",
        "土曜日に友だちと駅で会いました。",
        "朝、駅まで歩いて行きました。",
        "私は来週、日本語のテストがあります。"
    ]

}
# -------------------------
# 📌 랜덤 예문 설정 (최초 실행 시 또는 새로고침 시)
# -------------------------
if "target_sentence" not in st.session_state:
    st.session_state.target_sentence = random.choice(example_sentences[language])

if st.button("🔁 예문 새로고침"):
    st.session_state.target_sentence = random.choice(example_sentences[language])

# -------------------------
# 📝 문장 출력
# -------------------------
st.title("🎤 영어 발음 피드백 웹앱")
st.subheader("📘 오늘의 연습 문장:")
st.write(f"**{st.session_state.target_sentence}**")

# -------------------------
# 🎙️ 녹음 설정 및 시작
# -------------------------
DURATION = 8.5  # 녹음 시간 (초)
FS = 44100    # 샘플링 주파수

if st.button("🎙 녹음 시작"):
    st.write("🎙 녹음 중입니다. 말하세요...")
    recording = sd.rec(int(DURATION * FS), samplerate=FS, channels=1)
    sd.wait()
    filename = "recorded_audio.wav"
    wavio.write(filename, recording, FS, sampwidth=2)
    st.success("✅ 녹음 완료! 음성 파일이 저장되었습니다.")

# -------------------------
# 🧠 Whisper로 STT 변환
# -------------------------
model = whisper.load_model("base")  # 필요 시 "small"로 교체

if st.button("🧠 Whisper로 음성 인식 시작"):
    st.info("🌀 음성을 텍스트로 변환 중입니다...")
    try:
        result = model.transcribe("recorded_audio.wav")
        recognized_text = result["text"]

        st.subheader("🗣 Whisper 결과:")
        st.write(recognized_text)

        # -------------------------
        # 📊 발음 정확도 분석
        # -------------------------
        st.subheader("📊 발음 정확도 분석")

        recognized_clean = recognized_text.strip().lower()
        target_clean = st.session_state.target_sentence.strip().lower()

        distance = Levenshtein.distance(recognized_clean, target_clean)
        max_len = max(len(recognized_clean), len(target_clean))
        accuracy = round((1 - distance / max_len) * 100)

        st.write(f"🎯 정확도 점수: **{accuracy}%**")

        if accuracy >= 90:
            st.success("🟢 훌륭해요! 완벽한 발음이었어요.")
        elif accuracy >= 70:
            st.info("🟡 거의 정확했어요. 아주 약간의 수정만 필요해요.")
        else:
            st.warning("🔴 조금 더 연습이 필요해요. 다시 도전해볼까요?")

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

# -------------------------
# 🧩 단어별 피드백
# -------------------------

# 조건 추가: recognized_text가 정의되어 있고, 비어있지 않을 때만 실행
if 'recognized_text' in locals() and recognized_text.strip():
    target_clean = st.session_state.target_sentence.strip().lower()
    recognized_clean = recognized_text.strip().lower()

    st.subheader("🧩 단어별 발음 피드백")

    import difflib
    target_words = target_clean.split()
    recognized_words = recognized_clean.split()

    matcher = difflib.SequenceMatcher(None, target_words, recognized_words)
    diff_result = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == "equal":
            for word in target_words[i1:i2]:
                diff_result.append(f"✅ {word}")
        elif opcode == "replace":
            for word in target_words[i1:i2]:
                diff_result.append(f"❌ (틀림) {word}")
            for word in recognized_words[j1:j2]:
                diff_result.append(f"👉 (대신 말한 것) {word}")
        elif opcode == "delete":
            for word in target_words[i1:i2]:
                diff_result.append(f"❌ (누락됨) {word}")
        elif opcode == "insert":
            for word in recognized_words[j1:j2]:
                diff_result.append(f"➕ (추가됨) {word}")

    for feedback in diff_result:
        st.write(feedback)



# 명령어: python3 -m streamlit run app.py
