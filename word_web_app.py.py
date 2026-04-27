import streamlit as st
import pandas as pd
import random
import time

# --- ページ設定（スマホでスクロール不要なサイズ感） ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    .stButton button { 
        width: 100%; 
        margin-bottom: -20px; 
        padding: 0.4rem; 
        font-size: 0.9rem;
    }
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
    st.session_state.total_count = len(st.session_state.words) # 全体の母数（例：100問）
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = []
    st.session_state.mastered_count = 0 # 累計正解数
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

# ラウンド終了後の結果表示（ここで正答率を計算）
if st.session_state.show_result:
    # 累計正解数 ÷ 全体の母数 で計算（例：90/100=90%, 次に+5問で95/100=95%）
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    
    st.subheader(f"Round {st.session_state.round} 終了")
    st.metric("累計正答率", f"{accuracy:.0f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success(f"100%達成！全{st.session_state.total_count}問をマスターしました！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        st.info(f"現在 {st.session_state.mastered_count} / {st.session_state.total_count} 問正解")
        st.write(f"残り {len(st.session_state.wrong_list)} 問に再挑戦します。")
        if st.button("次のラウンドへ"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            next_question()
            st.rerun()

# クイズ出題画面
else:
    if st.session_state.current_question is None:
        next_question()

    q = st.session_state.current_question
    
    # 今のラウンドの残り枚数表示
    st.write(f"このRの残り: {len(st.session_state.queue) + 1}問 / 累計正解: {st.session_state.mastered_count}問")
    st.subheader(f"「{q['word']}」の意味は？")

    # 選択肢5つ
    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    for opt in options:
        if st.button(opt):
            if opt == q['meaning']:
                st.toast("正解！", icon="✅")
                st.session_state.mastered_count += 1
                next_question()
                st.rerun()
            else:
                st.error(f"正解は「{q['meaning']}」")
                if q not in st.session_state.wrong_list:
                    st.session_state.wrong_list.append(q)
                # 間違えても止まらず、1.5秒後に自動で次の問題へ
                time.sleep(1.5)
                next_question()
                st.rerun()
