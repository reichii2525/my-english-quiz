import streamlit as st
import pandas as pd
import random
import time

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

def next_question():
    if not st.session_state.queue:
        st.session_state.show_result = True
        st.session_state.current_q = None
    else:
        st.session_state.current_q = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))

if st.session_state.current_q is None and not st.session_state.show_result:
    next_question()

# --- メイン画面 ---
st.title(f"英単語クイズ Round {st.session_state.round}")

# 1. 【リザルト画面】
if st.session_state.show_result:
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    st.subheader(f"Round {st.session_state.round} 終了")
    st.metric("累計正答率", f"{accuracy:.1f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("🎉 全問正解！100%達成です！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        st.info(f"不正解だった {len(st.session_state.wrong_list)} 問を次のラウンドで出題します。")
        if st.button("次のラウンドを開始"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            next_question()
            st.rerun()

# 2. 【クイズ画面】
else:
    q = st.session_state.current_q
    st.markdown(f"<div class='status-text'>残り: {len(st.session_state.queue) + 1}問 / 全体正解: {st.session_state.mastered_count}問</div>", unsafe_allow_html=True)
    st.subheader(f"「{q['word']}」の意味は？")

    # 選択肢の生成
    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    # ボタンを配置するプレースホルダー
    placeholder = st.empty()
    
    with placeholder.container():
        for opt in options:
            if st.button(opt, key=f"r{st.session_state.round}_{q['word']}_{opt}"):
                if opt == q['meaning']:
                    # --- 【正解】 ---
                    st.success("〇 正解！")
                    st.session_state.mastered_count += 1
                    # 正解は一瞬（0.3秒）で次へ
                    time.sleep(0.3)
                    next_question()
                    st.rerun()
                else:
                    # --- 【不正解】 ---
                    st.session_state.wrong_list.append(q)
                    # 赤い枠で正解を表示
                    st.error(f"× 不正解！ 正解は：{q['meaning']}")
                    # ここで3秒間停止。石濱さんが正解を確認できるようにします。
                    time.sleep(3.0)
                    next_question()
                    st.rerun()
