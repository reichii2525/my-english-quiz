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

# 【重要】次の問題を準備し、現在の問題を破棄する関数
def move_to_next():
    if not st.session_state.queue:
        st.session_state.show_result = True
        st.session_state.current_q = None
    else:
        # 完全にランダムに一問取り出し（popするのでリストからは消える）
        st.session_state.current_q = st.session_state.queue.pop(random.randrange(len(st.session_state.queue)))

# 初回起動
if st.session_state.current_q is None and not st.session_state.show_result:
    move_to_next()

# --- メイン画面 ---
st.title(f"英単語クイズ Round {st.session_state.round}")

if st.session_state.show_result:
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
        if st.button("次のラウンド（不正解分のみ）を開始"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            move_to_next()
            st.rerun()

else:
    q = st.session_state.current_q
    st.markdown(f"<div class='status-text'>残り: {len(st.session_state.queue) + 1}問 / 全体正解: {st.session_state.mastered_count}問</div>", unsafe_allow_html=True)
    st.subheader(f"「{q['word']}」")

    # 選択肢の生成
    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    for opt in options:
        # keyに単語名を入れることで、確実に画面をリセットさせる
        if st.button(opt, key=f"r{st.session_state.round}_{q['word']}_{opt}"):
            if opt == q['meaning']:
                st.success("〇 正解！")
                st.session_state.mastered_count += 1
                # 正解時はすぐ次へ
                time.sleep(0.4)
            else:
                # 不正解リストに保存して、画面に意味を表示
                st.session_state.wrong_list.append(q)
                st.error(f"× 不正解！ 正解は：{q['meaning']}")
                # 意味を確認するために3秒止まる
                time.sleep(3.0)
            
            # 判定が終わったら、問答無用で次の問題へ
            move_to_next()
            st.rerun()
