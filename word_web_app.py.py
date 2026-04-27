import streamlit as st
import pandas as pd
import random
import time

# --- ページ設定（スマホ最適化） ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    .stButton button { width: 100%; margin-bottom: -18px; padding: 0.4rem; font-size: 0.9rem; }
    h1 { font-size: 1.1rem !important; margin-bottom: -10px; }
    .stSubheader { font-size: 1.2rem !important; margin-top: -5px; }
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
    st.session_state.total_count = len(st.session_state.words) # 全体の母数
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = [] 
    st.session_state.mastered_count = 0 
    st.session_state.current_question = None
    st.session_state.round = 1
    st.session_state.show_result = False
    st.session_state.answer_feedback = None # 〇か×の判定保持用

def next_question():
    if not st.session_state.queue:
        st.session_state.show_result = True
        st.session_state.current_question = None
    else:
        st.session_state.current_question = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))
    st.session_state.answer_feedback = None

# --- メイン画面 ---
st.title(f"英単語クイズ R{st.session_state.round}")

# ラウンド終了後の結果表示
if st.session_state.show_result:
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    st.subheader(f"Round {st.session_state.round} 終了")
    st.metric("累計正答率", f"{accuracy:.0f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success(f"100%達成！全{st.session_state.total_count}問を完了！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        st.write(f"累計正解: {st.session_state.mastered_count} / {st.session_state.total_count}")
        st.info(f"不正解だった {len(st.session_state.wrong_list)} 問を次のRoundで出題します。")
        if st.button("次のRoundへ進む"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            next_question()
            st.rerun()

# クイズ画面
else:
    if st.session_state.current_question is None:
        next_question()

    q = st.session_state.current_question
    st.write(f"残り: {len(st.session_state.queue) + 1}問 / 全体正解: {st.session_state.mastered_count}問")
    st.subheader(f"「{q['word']}」の意味は？")

    # 選択肢の生成
    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    # 判定前：選択肢を表示
    if st.session_state.answer_feedback is None:
        for opt in options:
            if st.button(opt):
                if opt == q['meaning']:
                    st.session_state.mastered_count += 1
                    st.session_state.answer_feedback = "〇 正解！"
                    st.rerun()
                else:
                    st.session_state.wrong_list.append(q)
                    st.session_state.answer_feedback = f"× 不正解！ 正解は：{q['meaning']}"
                    st.rerun()
    
    # 判定後：〇か×を表示して「次へ」進む
    else:
        if "〇" in st.session_state.answer_feedback:
            st.success(st.session_state.answer_feedback)
        else:
            st.error(st.session_state.answer_feedback)
            
        if st.button("次の問題へ"):
            next_question()
            st.rerun()
