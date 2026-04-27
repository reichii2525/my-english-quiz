import streamlit as st
import pandas as pd
import random

# --- ページ設定 ---
st.set_page_config(page_title="英単語クイズ", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    .stButton button { width: 100%; margin-bottom: -18px; padding: 0.4rem; font-size: 0.9rem; }
    h1 { font-size: 1.1rem !important; margin-bottom: -10px; }
    .stSubheader { font-size: 1.2rem !important; margin-top: -10px; }
    div[data-testid="stText"] { font-size: 0.8rem; margin-bottom: -15px; }
    </style>
""", unsafe_allow_html=True)

# --- データ読み込み ---
@st.cache_data
def load_data():
    df = pd.read_csv('英単語 - シート1.csv')
    df.columns = ['word', 'meaning'] + list(df.columns[2:])
    return df.to_dict('records')

# --- セッション初期化 ---
if 'words' not in st.session_state:
    st.session_state.words = load_data()
    st.session_state.queue = st.session_state.words.copy()
    st.session_state.wrong_list = []
    st.session_state.mastered = set()  # ←重要
    st.session_state.total_count = len(st.session_state.words)
    st.session_state.current_question = None
    st.session_state.round = 1
    st.session_state.show_result = False

# --- 次の問題 ---
def next_question():
    if not st.session_state.queue:
        st.session_state.show_result = True
    else:
        st.session_state.current_question = st.session_state.queue.pop(
            random.randrange(len(st.session_state.queue))
        )

# --- タイトル ---
st.title(f"英単語クイズ R{st.session_state.round}")

# =========================
# ✅ ラウンド終了画面
# =========================
if st.session_state.show_result:

    accuracy = (len(st.session_state.mastered) / st.session_state.total_count) * 100

    st.subheader(f"Round {st.session_state.round} 終了")
    st.metric("現在の総正答率", f"{accuracy:.1f}%")

    if not st.session_state.wrong_list:
        st.balloons()
        st.success(f"全{st.session_state.total_count}問、完全制覇！")

        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()

    else:
        st.write(f"残り {len(st.session_state.wrong_list)} 問")

        if st.button("間違えた問題に再挑戦"):
            st.session_state.queue = st.session_state.wrong_list.copy()
            st.session_state.wrong_list = []
            st.session_state.round += 1
            st.session_state.show_result = False
            st.session_state.current_question = None
            st.rerun()

# =========================
# ✅ クイズ画面
# =========================
else:
    if st.session_state.current_question is None:
        next_question()

    q = st.session_state.current_question

    st.write(
        f"このラウンド: 残り {len(st.session_state.queue)+1}問 / "
        f"累計正解: {len(st.session_state.mastered)}問"
    )

    st.subheader(f"「{q['word']}」の意味は？")

    # 選択肢作成
    all_meanings = [w['meaning'] for w in st.session_state.words]
    wrong_options = random.sample(
        [m for m in all_meanings if m != q['meaning']],
        min(len(all_meanings)-1, 4)
    )
    options = random.sample(wrong_options + [q['meaning']], len(wrong_options) + 1)

    # ボタン表示
    for opt in options:
        if st.button(opt):

            # =========================
            # ✅ 正解
            # =========================
            if opt == q['meaning']:
                st.success("〇 正解！")
                st.write(f"意味：{q['meaning']}")

                # ★ ここが最重要（累計管理）
                st.session_state.mastered.add((q['word'], q['meaning']))

                next_question()
                st.rerun()

            # =========================
            # ❌ 不正解
            # =========================
            else:
                st.error("× 不正解")
                st.write(f"正解：{q['meaning']}")

                if q not in st.session_state.wrong_list:
                    st.session_state.wrong_list.append(q)

                if st.button("次へ"):
                    next_question()
                    st.rerun()
