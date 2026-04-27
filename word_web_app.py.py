import streamlit as st
import pandas as pd
import random

# --- ページ設定（スマホ最適化） ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; }
    .stButton button { width: 100%; margin-bottom: -15px; padding: 0.6rem; font-size: 1rem; }
    h1 { font-size: 1.2rem !important; }
    .status-text { font-size: 0.8rem; color: gray; }
    </style>
    """, unsafe_allow_html=True)

# --- データの読み込み ---
@st.cache_data
def load_data():
    # ファイル名は以前の指示通り
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
    st.session_state.is_wrong_mode = False # 不正解確認モードかどうか

def next_question():
    if not st.session_state.queue:
        st.session_state.show_result = True
        st.session_state.current_q = None
    else:
        st.session_state.current_q = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))
    st.session_state.is_wrong_mode = False

# 初回起動
if st.session_state.current_q is None and not st.session_state.show_result:
    next_question()

# --- メイン表示 ---
st.title(f"英単語クイズ R{st.session_state.round}")

# 1. 【結果表示】
if st.session_state.show_result:
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    st.metric("累計正答率", f"{accuracy:.0f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("🎉 全問マスター！おめでとうございます！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        st.info(f"不正解が {len(st.session_state.wrong_list)} 問あります。")
        if st.button("次のラウンド（不正解分）へ"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            next_question()
            st.rerun()

# 2. 【不正解確認モード】
elif st.session_state.is_wrong_mode:
    q = st.session_state.current_q
    st.error("× 不正解")
    st.write(f"### 単語: {q['word']}")
    st.write(f"### 正解: **{q['meaning']}**")
    st.write("---")
    
    # このボタンを押すまで、画面は絶対に動きません
    if st.button("確認しました（次の問題へ）"):
        next_question()
        st.rerun()

# 3. 【通常出題モード】
else:
    q = st.session_state.current_q
    st.markdown(f"<p class='status-text'>累計正解: {st.session_state.mastered_count} / {st.session_state.total_count}</p>", unsafe_allow_html=True)
    st.subheader(f"「{q['word']}」の意味は？")

    # 選択肢の生成
    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    for opt in options:
        if st.button(opt, key=f"q{st.session_state.round}_{q['word']}_{opt}"):
            if opt == q['meaning']:
                # 正解なら即、次の問題へ（石濱さんの手間を減らすため）
                st.session_state.mastered_count += 1
                next_question()
                st.rerun()
            else:
                # 不正解なら確認画面モードへ切り替え
                st.session_state.wrong_list.append(q)
                st.session_state.is_wrong_mode = True
                st.rerun()
