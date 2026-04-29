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

# --- セッション状態（データ）の初期化 ---
if 'words' not in st.session_state:
    st.session_state.words = load_data()
    st.session_state.total_count = len(st.session_state.words)
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = []
    st.session_state.mastered_count = 0
    st.session_state.round = 1
    st.session_state.current_q = None
    # ★ここが重要：「ask（出題）」か「feedback（判定）」か「result（結果）」かを管理
    st.session_state.step = 'ask' 
    st.session_state.feedback_type = ""

# --- 次の問題を用意する関数 ---
def move_to_next():
    if not st.session_state.queue:
        st.session_state.step = 'result'
        st.session_state.current_q = None
    else:
        st.session_state.current_q = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))
        # 選択肢をこのタイミングで1回だけ作り、保存する（ボタンの誤作動を防ぐため）
        q = st.session_state.current_q
        all_meanings = [w['meaning'] for w in st.session_state.words]
        wrong_opts = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
        st.session_state.current_options = random.sample(wrong_opts + [q['meaning']], len(wrong_opts) + 1)

# 初回起動時
if st.session_state.current_q is None and st.session_state.step != 'result':
    move_to_next()

# --- メイン画面 ---
st.title(f"英単語クイズ Round {st.session_state.round}")

# 1. 【結果画面】全問終わったとき
if st.session_state.step == 'result':
    accuracy = (st.session_state.mastered_count / st.session_state.total_count) * 100
    st.subheader(f"Round {st.session_state.round} 終了")
    st.metric("累計正答率", f"{accuracy:.1f}%")
    
    if not st.session_state.wrong_list:
        st.balloons()
        st.success("🎉 100%達成！おめでとうございます！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        st.info(f"不正解だった {len(st.session_state.wrong_list)} 問を次のラウンドで出題します。")
        if st.button("次のラウンド（不正解分のみ）を開始"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.step = 'ask'
            move_to_next()
            st.rerun()

# 2. 【判定画面】ボタンを押した直後に表示され、自動で進む
elif st.session_state.step == 'feedback':
    q = st.session_state.current_q
    st.markdown(f"<div class='status-text'>残り: {len(st.session_state.queue) + 1}問 / 全体正解: {st.session_state.mastered_count}問</div>", unsafe_allow_html=True)
    st.subheader(f"「{q['word']}」")

    if st.session_state.feedback_type == 'correct':
        st.success("〇 正解！")
        time.sleep(0.5) # 正解なら0.5秒だけ待つ
    else:
        st.error(f"× 不正解！ 正解は：{q['meaning']}")
        time.sleep(3.0) # 不正解なら意味を確認できるよう3秒待つ
    
    # 待ち時間が終わったら、自動的に次の問題へ進む処理
    move_to_next()
    st.session_state.step = 'ask'
    st.rerun()

# 3. 【クイズ出題画面】
elif st.session_state.step == 'ask':
    q = st.session_state.current_q
    st.markdown(f"<div class='status-text'>残り: {len(st.session_state.queue) + 1}問 / 全体正解: {st.session_state.mastered_count}問</div>", unsafe_allow_html=True)
    st.subheader(f"「{q['word']}」の意味は？")

    for opt in st.session_state.current_options:
        # ボタンが押されたときの処理
        if st.button(opt, key=f"btn_{opt}"):
            if opt == q['meaning']:
                st.session_state.mastered_count += 1
                st.session_state.feedback_type = 'correct'
            else:
                st.session_state.wrong_list.append(q)
                st.session_state.feedback_type = 'wrong'
            
            # 正解・不正解にかかわらず、必ず【判定画面】へ切り替える
            st.session_state.step = 'feedback'
            st.rerun()
