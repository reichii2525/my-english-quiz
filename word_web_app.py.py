import streamlit as st
import pandas as pd
import random
import time

# --- ページ設定 ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; }
    .stButton button { width: 100%; margin-bottom: -15px; padding: 0.5rem; font-size: 1rem; }
    h1 { font-size: 1.2rem !important; }
    .stAlert { margin-top: 10px; }
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

# 次の問題を準備する関数
def prepare_next():
    if not st.session_state.queue:
        st.session_state.show_result = True
        st.session_state.current_q = None
    else:
        st.session_state.current_q = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))

if st.session_state.current_q is None and not st.session_state.show_result:
    prepare_next()

# --- メイン画面 ---
st.title(f"英単語クイズ R{st.session_state.round}")

if st.session_state.show_result:
    # 累計正答率の計算
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    st.subheader(f"Round {st.session_state.round} 終了")
    st.metric("累計正答率", f"{accuracy:.0f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("100%達成！おめでとうございます！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        st.write(f"累計正解: {st.session_state.mastered_count} / {st.session_state.total_count}")
        if st.button("次のRound（不正解分）を開始"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            prepare_next()
            st.rerun()

else:
    q = st.session_state.current_q
    st.write(f"残り: {len(st.session_state.queue) + 1}問 / 全体正解: {st.session_state.mastered_count}問")
    st.subheader(f"「{q['word']}」")

    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    # ボタンを配置するエリア（回答したら消える）
    placeholder = st.empty()
    
    with placeholder.container():
        for opt in options:
            if st.button(opt, key=f"{q['word']}_{opt}"):
                # 1. 判定を画面に表示
                if opt == q['meaning']:
                    st.success("〇 正解！")
                    st.session_state.mastered_count += 1
                    wait_time = 0.8  # 正解時は少し早めに次へ
                else:
                    st.session_state.wrong_list.append(q)
                    # ここで「×」と「意味」を確実に出す
                    st.error(f"× 不正解！ 正解は：{q['meaning']}")
                    wait_time = 2.5  # 不正解時はしっかり確認できるよう長めに停止

                # 2. 次の問題を「裏で」準備
                prepare_next()
                
                # 3. 指定した時間だけ画面を止めて、判定を見せる
                time.sleep(wait_time)
                
                # 4. 画面をリフレッシュして次の問題へ
                st.rerun()
