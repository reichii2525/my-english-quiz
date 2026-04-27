import streamlit as st
import pandas as pd
import random

# --- ページ設定（スマホ最適化） ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stButton button { width: 100%; margin-bottom: -15px; }
    h1 { font-size: 1.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- データの読み込み（名前が何でも動く設定） ---
@st.cache_data
def load_data():
    # CSVを読み込む
    df = pd.read_csv('英単語 - シート1.csv')
    # 1列目をword、2列目をmeaningと強制的に決める（これで日本語エラーを防ぐ）
    df.columns = ['word', 'meaning'] + list(df.columns[2:])
    return df.to_dict('records')

if 'words' not in st.session_state:
    st.session_state.words = load_data()
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = []
    st.session_state.current_question = None
    st.session_state.round = 1

def next_question():
    if not st.session_state.queue:
        if not st.session_state.wrong_list:
            st.session_state.finished = True
        else:
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.current_question = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))
    else:
        st.session_state.current_question = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))

# --- メイン画面 ---
st.title(f"英単語クイズ Round {st.session_state.round}")

if 'finished' in st.session_state and st.session_state.finished:
    st.balloons()
    st.success("全問正解！お疲れ様でした！")
    if st.button("もう一度最初から"):
        st.session_state.clear()
        st.rerun()
else:
    if st.session_state.current_question is None:
        next_question()

    q = st.session_state.current_question
    st.write(f"残り: {len(st.session_state.queue) + 1}問 / ミス: {len(st.session_state.wrong_list)}問")
    st.subheader(f"「{q['word']}」の意味は？")

    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 3))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    for opt in options:
        if st.button(opt):
            if opt == q['meaning']:
                st.toast("正解！")
                next_question()
                st.rerun()
            else:
                st.error(f"正解は「{q['meaning']}」")
                if q not in st.session_state.wrong_list:
                    st.session_state.wrong_list.append(q)
                if st.button("次へ"):
                    next_question()
                    st.rerun()
