import streamlit as st
import pandas as pd
import random
import os

# ページの設定（スマホで見やすいようにタイトルなどを設定）
st.set_page_config(page_title="英単語マスター", page_icon="📝")

# スタイル調整（ボタンを大きく、中央寄せに）
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        font-size: 20px;
        height: 3em;
        margin-bottom: 10px;
    }
    .question-text {
        font-size: 32px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# データの読み込み
@st.cache_data
def load_data():
    file_path = '英単語 - シート1.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, header=None, names=['english', 'japanese'], encoding='utf-8-sig')
        return df.to_dict('records')
    return []

# セッション状態（クイズの進行状況）の管理
if 'pool' not in st.session_state:
    word_list = load_data()
    st.session_state.pool = word_list.copy()
    st.session_state.all_japanese = [w['japanese'] for w in word_list]
    st.session_state.current_question = None
    st.session_state.options = []
    st.session_state.message = ""
    st.session_state.msg_type = "info"

def next_question():
    if st.session_state.pool:
        st.session_state.current_question = random.choice(st.session_state.pool)
        options = [st.session_state.current_question['japanese']]
        others = [j for j in st.session_state.all_japanese if j != st.session_state.current_question['japanese']]
        options.extend(random.sample(others, min(len(others), 4)))
        random.shuffle(options)
        st.session_state.options = options
        st.session_state.message = ""

# 初回起動時
if st.session_state.current_question is None:
    next_question()

# メイン画面
st.title("🚀 英単語マスター")

if not st.session_state.pool:
    st.balloons()
    st.success("全問正解！お疲れ様でした！")
    if st.button("もう一度最初から"):
        st.session_state.pool = load_data().copy()
        next_question()
        st.rerun()
else:
    st.write(f"残り: {len(st.session_state.pool)} 問")
    
    # 問題表示
    st.markdown(f'<p class="question-text">{st.session_state.current_question["english"]}</p>', unsafe_allow_html=True)

    # 選択肢ボタン
    for i, opt in enumerate(st.session_state.options):
        if st.button(opt, key=f"btn_{i}"):
            if opt == st.session_state.current_question['japanese']:
                st.session_state.pool.remove(st.session_state.current_question)
                st.session_state.message = f"〇 正解！ 「{opt}」"
                st.session_state.msg_type = "success"
                next_question()
                st.rerun()
            else:
                st.session_state.message = f"× 不正解（正解: {st.session_state.current_question['japanese']}）"
                st.session_state.msg_type = "error"
                next_question()
                st.rerun()

# 結果表示
if st.session_state.message:
    if st.session_state.msg_type == "success":
        st.success(st.session_state.message)
    else:
        st.error(st.session_state.message)