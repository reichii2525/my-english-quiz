import streamlit as st
import pandas as pd
import random
import time
from gtts import gTTS
import io

# --- ページ設定 ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stButton button { width: 100%; padding: 0.8rem; font-size: 1.1rem; }
    .status-text { font-size: 1rem; color: #555; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- データの読み込み ---
def load_data():
    df = pd.read_csv('英単語 - シート1.csv').dropna(how='all')
    df.columns = ['word', 'meaning'] + list(df.columns[2:])
    return df.to_dict('records')

# --- 音声生成関数 ---
def get_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- セッション状態の初期化 ---
if 'words' not in st.session_state:
    st.session_state.words = load_data()
    st.session_state.total_count = len(st.session_state.words)
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = []
    st.session_state.mastered_count = 0
    st.session_state.round = 1
    st.session_state.current_q = None
    st.session_state.step = 'ask' 
    st.session_state.feedback_type = ""

# --- 次の問題を用意する関数 ---
def move_to_next():
    if not st.session_state.queue:
        st.session_state.step = 'result'
        st.session_state.current_q = None
    else:
        st.session_state.current_q = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))
        q = st.session_state.current_q
        all_meanings = [w['meaning'] for w in st.session_state.words]
        wrong_opts = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
        st.session_state.current_options = random.sample(wrong_opts + [q['meaning']], len(wrong_opts) + 1)

# 初回起動
if st.session_state.current_q is None and st.session_state.step != 'result':
    move_to_next()

# --- メイン画面 ---
st.title(f"英単語クイズ Round {st.session_state.round}")

# 1. 【結果画面】
if st.session_state.step == 'result':
    accuracy = (st.session_state.mastered_count / st.session_state.total_count * 100) if st.session_state.total_count > 0 else 0
    st.subheader(f"Round {st.session_state.round} 終了")
    st.write(f"全 {st.session_state.total_count} 問中、{st.session_state.mastered_count} 問正解")
    st.metric("累計正答率", f"{accuracy:.1f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("🎉 全問マスター達成！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        if st.button("次のラウンド（不正解分のみ）を開始"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.step = 'ask'
            move_to_next()
            st.rerun()

# 2. 【判定画面】
elif st.session_state.step == 'feedback':
    q = st.session_state.current_q
    if st.session_state.feedback_type == 'correct':
        st.success("〇 正解！")
        time.sleep(0.5)
    else:
        st.error(f"× 不正解！ 正解は：{q['meaning']}")
        time.sleep(3.0)
    
    st.session_state.step = 'ask'
    move_to_next()
    st.rerun()

# 3. 【出題画面】
elif st.session_state.step == 'ask':
    q = st.session_state.current_q
    st.markdown(f"<div class='status-text'>Round内残り: {len(st.session_state.queue) + 1}問 / 全 {st.session_state.total_count}問中 {st.session_state.mastered_count}問正解</div>", unsafe_allow_html=True)
    
    # === 追加：音声プレイヤー機能 ===
    audio_data = get_audio(q['word'])
    st.audio(audio_data, format="audio/mp3", autoplay=True)

    st.subheader(f"「{q['word']}」")

    for opt in st.session_state.current_options:
        if st.button(opt, key=f"btn_{st.session_state.round}_{len(st.session_state.queue)}_{opt}"):
            if opt == q['meaning']:
                st.session_state.mastered_count += 1
                st.session_state.feedback_type = 'correct'
            else:
                st.session_state.wrong_list.append(q)
                st.session_state.feedback_type = 'wrong'
            
            st.session_state.step = 'feedback'
            st.rerun()
