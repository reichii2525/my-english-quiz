import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; }
    .stButton button { width: 100%; margin-bottom: -15px; padding: 0.7rem; font-size: 1.1rem; }
    h1 { font-size: 1.2rem !important; }
    .status-text { font-size: 0.8rem; color: gray; }
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
    st.session_state.total_count = len(st.session_state.words)
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = []
    st.session_state.mastered_count = 0
    st.session_state.round = 1
    st.session_state.show_result = False
    st.session_state.current_q = None
    # 状態管理フラグ
    st.session_state.is_feedback_mode = False 

def next_question():
    if not st.session_state.queue:
        st.session_state.show_result = True
        st.session_state.current_q = None
    else:
        st.session_state.current_q = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))
    st.session_state.is_feedback_mode = False

# 初回セットアップ
if st.session_state.current_q is None and not st.session_state.show_result:
    next_question()

# --- メイン画面 ---
st.title(f"英単語クイズ R{st.session_state.round}")

# 1. 【全問解いた後の結果画面】
if st.session_state.show_result:
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    st.metric("累計正答率", f"{accuracy:.0f}%")
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("🎉 100%達成！おめでとうございます！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        if st.button("次のRound（不正解分）へ"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            next_question()
            st.rerun()

# 2. 【不正解の判定だけを見せる専用画面】
elif st.session_state.is_feedback_mode:
    q = st.session_state.current_q
    st.error("× 不正解")
    st.markdown(f"### 単語: {q['word']}")
    st.markdown(f"### 正解: {q['meaning']}")
    st.write("---")
    # このボタンを押すまで、絶対に次の問題には進みません
    if st.button("確認して次の問題へ"):
        next_question()
        st.rerun()

# 3. 【通常のクイズ回答画面】
else:
    q = st.session_state.current_q
    st.markdown(f"<p class='status-text'>累計正解: {st.session_state.mastered_count} / {st.session_state.total_count}</p>", unsafe_allow_html=True)
    st.subheader(f"「{q['word']}」の意味は？")

    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    for opt in options:
        if st.button(opt, key=f"{q['word']}_{opt}"):
            if opt == q['meaning']:
                # 正解ならボタンを出さずにそのまま次へ
                st.session_state.mastered_count += 1
                next_question()
                st.rerun()
            else:
                # 不正解なら「判定専用画面」へ強制ジャンプ
                st.session_state.wrong_list.append(q)
                st.session_state.is_feedback_mode = True
                st.rerun()
