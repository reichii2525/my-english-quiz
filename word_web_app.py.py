import streamlit as st
import pandas as pd
import random
import time

# --- ページ設定（スマホ最適化） ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    .stButton button { 
        width: 100%; 
        margin-bottom: -18px; 
        padding: 0.5rem; 
        font-size: 1rem;
    }
    h1 { font-size: 1.1rem !important; margin-bottom: -10px; }
    .stSubheader { font-size: 1.3rem !important; margin-top: -5px; color: #31333F; }
    </style>
    """, unsafe_allow_html=True)

# --- データの読み込み ---
@st.cache_data
def load_data():
    df = pd.read_csv('英単語 - シート1.csv')
    df.columns = ['word', 'meaning'] + list(df.columns[2:])
    return df.to_dict('records')

if 'words' not in st.session_state:
    st.session_state.words = load_data()
    st.session_state.total_count = len(st.session_state.words)
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = []
    st.session_state.mastered_count = 0
    st.session_state.current_question = None
    st.session_state.round = 1
    st.session_state.show_result = False

def next_question():
    if not st.session_state.queue:
        st.session_state.show_result = True
        st.session_state.current_question = None
    else:
        st.session_state.current_question = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))

# --- メイン画面 ---
st.title(f"英単語クイズ R{st.session_state.round}")

if st.session_state.show_result:
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    st.subheader(f"Round {st.session_state.round} 終了")
    st.metric("累計正答率", f"{accuracy:.0f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("100%達成！素晴らしいです！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        st.write(f"累計正解: {st.session_state.mastered_count} / {st.session_state.total_count}")
        st.info(f"不正解だった {len(st.session_state.wrong_list)} 問を次のラウンドで出題します。")
        if st.button("次のラウンドを開始"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            next_question()
            st.rerun()

else:
    if st.session_state.current_question is None:
        next_question()

    q = st.session_state.current_question
    st.write(f"残り: {len(st.session_state.queue) + 1}問 / 累計正解: {st.session_state.mastered_count}問")
    st.subheader(f"「{q['word']}」")

    # 選択肢の生成
    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    # ボタンをクリックした瞬間に判定
    for opt in options:
        if st.button(opt, key=f"btn_{opt}"):
            if opt == q['meaning']:
                st.success("〇 正解！")
                st.session_state.mastered_count += 1
                # 正解時は一瞬（0.5秒）だけ表示して次へ
                time.sleep(0.5)
            else:
                st.session_state.wrong_list.append(q)
                st.error(f"× 不正解！ 正解は：{q['meaning']}")
                # 不正解時はしっかり確認できるよう1.5秒待ってから次へ
                time.sleep(1.5)
            
            next_question()
            st.rerun()
