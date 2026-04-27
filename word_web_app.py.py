import streamlit as st
import pandas as pd
import random

# --- ページ設定（スマホで見やすく） ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

# CSSで見た目をさらにコンパクトに調整
st.markdown("""
    <style>
    .stButton button { width: 100%; margin-bottom: -10px; }
    .reportview-container .main .block-container { padding-top: 1rem; }
    h1 { font-size: 1.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- データの読み込み ---
@st.cache_data
def load_data():
    df = pd.read_csv('英単語 - シート1.csv')
    return df.to_dict('records')

if 'words' not in st.session_state:
    st.session_state.words = load_data()
    # 出題待ちリスト（最初は全問）
    st.session_state.queue = st.session_state.words.copy()
    # 間違えた単語リスト
    st.session_state.wrong_list = []
    st.session_state.current_question = None
    st.session_state.round = 1

def next_question():
    if not st.session_state.queue:
        # 現在のラウンドが終了
        if not st.session_state.wrong_list:
            st.session_state.finished = True
        else:
            # 間違えた単語を次のラウンドの出題リストへ
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.current_question = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))
    else:
        st.session_state.current_question = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))

# --- メイン画面 ---
st.title(f"英単語クイズ (Round {st.session_state.round})")

if 'finished' in st.session_state and st.session_state.finished:
    st.balloons()
    st.success("全問正解です！お疲れ様でした！")
    if st.button("もう一度最初から解く"):
        st.session_state.clear()
        st.rerun()
else:
    if st.session_state.current_question is None:
        next_question()

    q = st.session_state.current_question
    
    # 残り問題数の表示
    st.write(f"残り: {len(st.session_state.queue) + 1}問 / ミス: {len(st.session_state.wrong_list)}問")
    
    # 出題
    st.subheader(f"「{q['単語']}」の意味は？")

    # 選択肢の作成（正解 + ランダムな3つ）
    all_meanings = [w['意味'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['意味']], 3)
    options = random.sample(wrong_options + [q['意味']], 4)

    # 判定
    for opt in options:
        if st.button(opt):
            if opt == q['意味']:
                st.toast("正解！", icon="✅")
                next_question()
                st.rerun()
            else:
                st.error(f"不正解... 正解は「{q['意味']}」でした")
                if q not in st.session_state.wrong_list:
                    st.session_state.wrong_list.append(q)
                if st.button("次の問題へ"):
                    next_question()
                    st.rerun()
