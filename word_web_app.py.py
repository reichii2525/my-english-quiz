import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; }
    .stButton button { width: 100%; margin-bottom: -15px; padding: 0.5rem; font-size: 1rem; }
    h1 { font-size: 1.2rem !important; }
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
    st.session_state.is_answered = False # 回答したかどうかのフラグ
    st.session_state.feedback_type = ""  # "correct" か "wrong" か

def next_question():
    if not st.session_state.queue:
        st.session_state.show_result = True
        st.session_state.current_q = None
    else:
        st.session_state.current_q = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))
    # 状態をリセット
    st.session_state.is_answered = False

if st.session_state.current_q is None and not st.session_state.show_result:
    next_question()

# --- メイン画面 ---
st.title(f"英単語クイズ R{st.session_state.round}")

# 結果発表画面
if st.session_state.show_result:
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    st.metric("累計正答率", f"{accuracy:.0f}%")
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("100%達成！")
        if st.button("最初から"):
            st.session_state.clear()
            st.rerun()
    else:
        if st.button("次のRound（不正解分）を開始"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            next_question()
            st.rerun()

# クイズ出題画面
else:
    q = st.session_state.current_q
    st.write(f"残り: {len(st.session_state.queue) + 1}問 / 全体正解: {st.session_state.mastered_count}問")
    st.subheader(f"「{q['word']}」")

    # 【回答前】選択肢ボタンを表示
    if not st.session_state.is_answered:
        all_meanings = [w['meaning'] for w in st.session_state.words]
        wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
        options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

        for opt in options:
            if st.button(opt, key=f"{q['word']}_{opt}"):
                st.session_state.is_answered = True
                if opt == q['meaning']:
                    st.session_state.mastered_count += 1
                    st.session_state.feedback_type = "correct"
                else:
                    st.session_state.wrong_list.append(q)
                    st.session_state.feedback_type = "wrong"
                st.rerun()

    # 【回答後】判定を表示。ここで画面を止めて「次へ」を待つ
    else:
        if st.session_state.feedback_type == "correct":
            st.success("〇 正解！")
        else:
            # 不正解なら確実に「×」と「意味」を表示
            st.error(f"× 不正解！ 正解は：{q['meaning']}")
            
        if st.button("次へ進む"):
            next_question()
            st.rerun()
