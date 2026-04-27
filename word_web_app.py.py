import streamlit as st
import pandas as pd
import random

# --- ページ設定（スマホ最適化） ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    .stButton button { width: 100%; margin-bottom: -18px; padding: 0.4rem; font-size: 0.9rem; }
    h1 { font-size: 1.1rem !important; margin-bottom: -10px; }
    .stSubheader { font-size: 1.2rem !important; margin-top: -10px; }
    div[data-testid="stText"] { font-size: 0.8rem; margin-bottom: -15px; }
    </style>
    """, unsafe_allow_html=True)

# --- データの読み込み ---
@st.cache_data
def load_data():
    df = pd.read_csv('英単語 - シート1.csv')
    df.columns = ['word', 'meaning'] + list(df.columns[2:])
    return df.to_dict('records')

# セッション状態の初期化
if 'words' not in st.session_state:
    st.session_state.words = load_data()
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = []
    st.session_state.correct_count = 0  # 今回のラウンドでの正解数
    st.session_state.total_in_round = len(st.session_state.queue) # ラウンド開始時の総数
    st.session_state.current_question = None
    st.session_state.round = 1
    st.session_state.show_result = False # 正答率表示フラグ

def next_question():
    if not st.session_state.queue:
        # ラウンド終了、正答率表示画面へ
        st.session_state.show_result = True
    else:
        st.session_state.current_question = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))

# --- メイン画面 ---
st.title(f"英単語クイズ R{st.session_state.round}")

# 正答率表示画面
if st.session_state.show_result:
    accuracy = (st.session_state.correct_count / st.session_state.total_in_round) * 100
    st.subheader(f"Round {st.session_state.round} 終了！")
    st.metric("今回の正答率", f"{accuracy:.1f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("全問正解です！パーフェクト！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        st.warning(f"{len(st.session_state.wrong_list)}問間違えました。次はこれだけを解きます！")
        if st.button("次のラウンドへ"):
            # 間違えたリストを次の出題リストにセット
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.total_in_round = len(st.session_state.queue)
            st.session_state.correct_count = 0
            st.session_state.round += 1
            st.session_state.show_result = False
            next_question()
            st.rerun()

# クイズ画面
else:
    if st.session_state.current_question is None:
        next_question()

    q = st.session_state.current_question
    st.write(f"残り: {len(st.session_state.queue) + 1}問 / 今回のミス: {len(st.session_state.wrong_list)}問")
    st.subheader(f"「{q['word']}」の意味は？")

    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    for opt in options:
        if st.button(opt):
            if opt == q['meaning']:
                st.toast("正解！", icon="✅")
                st.session_state.correct_count += 1
                next_question()
                st.rerun()
            else:
                st.error(f"正解は「{q['meaning']}」")
                if q not in st.session_state.wrong_list:
                    st.session_state.wrong_list.append(q)
                if st.button("次へ"):
                    next_question()
                    st.rerun()
