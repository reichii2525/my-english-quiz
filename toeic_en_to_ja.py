import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# --- ページ設定 ---
st.set_page_config(page_title="TOEIC英単語クイズ(英→日)", layout="centered")

# スタイル設定
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stButton button { width: 100%; padding: 0.8rem; font-size: 1.1rem; }
    .status-text { font-size: 1rem; color: #555; margin-bottom: 10px; background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- データの読み込み ---
def load_data():
    try:
        df = pd.read_csv('toeic.csv').dropna(how='all')
        df.columns = ['word', 'meaning'] + list(df.columns[2:])
        return df.to_dict('records')
    except Exception as e:
        st.error("CSVファイルの読み込みに失敗しました。ファイル名が 'toeic.csv' か確認してください。")
        return []

def get_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- セッション状態の初期化 ---
if 'en_words' not in st.session_state:
    st.session_state.en_words = load_data()
    st.session_state.en_total_count = len(st.session_state.en_words)
    st.session_state.en_queue = st.session_state.en_words.copy()
    st.session_state.en_wrong_list = []
    st.session_state.en_mastered_count = 0
    st.session_state.en_round = 1
    st.session_state.en_current_q = None
    st.session_state.en_step = 'ask'
    st.session_state.en_play_audio = False

# --- 次の問題を用意する関数 ---
def move_to_next():
    if not st.session_state.en_queue:
        st.session_state.en_step = 'result'
        st.session_state.en_current_q = None
    else:
        st.session_state.en_current_q = st.session_state.en_queue.pop(random.randrange(len(st.session_state.en_queue)))
        q = st.session_state.en_current_q
        all_meanings = [w['meaning'] for w in st.session_state.en_words]
        wrong_opts = random.sample([m for m in all_meanings if m != q['meaning']], min(len(all_meanings)-1, 4))
        st.session_state.en_current_options = random.sample(wrong_opts + [q['meaning']], len(wrong_opts) + 1)
        st.session_state.en_play_audio = True

if st.session_state.en_current_q is None and st.session_state.en_step != 'result':
    move_to_next()

st.title(f"TOEIC英単語クイズ(英→日) Round {st.session_state.en_round}")

# 1. 【結果画面】
if st.session_state.en_step == 'result':
    accuracy = (st.session_state.en_mastered_count / st.session_state.en_total_count * 100) if st.session_state.en_total_count > 0 else 0
    st.subheader(f"Round {st.session_state.en_round} 終了")
    st.write(f"全 {st.session_state.en_total_count} 問中、{st.session_state.en_mastered_count} 問正解")
    st.metric("累計正答率", f"{accuracy:.1f}%")
    
    if not st.session_state.en_wrong_list:
        st.balloons()
        st.success("🎉 全問正解達成！素晴らしいです！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        if st.button("次のラウンド（不正解分のみ）を開始"):
            st.session_state.en_queue = st.session_state.en_wrong_list.copy()
            st.session_state.en_wrong_list = []
            st.session_state.en_round += 1
            st.session_state.en_step = 'ask'
            move_to_next()
            st.rerun()

# 2. 【判定画面（不正解時）】
elif st.session_state.en_step == 'feedback_wrong':
    q = st.session_state.en_current_q
    st.error(f"× 不正解！ 正解は： **{q['meaning']}**")
    st.write(f"単語: {q['word']}")
    
    if st.button("確認して次の問題へ", type="primary"):
        st.session_state.en_step = 'ask'
        move_to_next()
        st.rerun()

# 3. 【出題画面】
elif st.session_state.en_step == 'ask':
    
    # 進行状況の表示
    remaining = len(st.session_state.en_queue) + 1
    st.markdown(f"""
        <div class='status-text'>
            <b>Round内残り:</b> {remaining}問 / 
            <b>全 {st.session_state.en_total_count}問中:</b> {st.session_state.en_mastered_count}問正解
        </div>
        """, unsafe_allow_html=True)

    q = st.session_state.en_current_q
    
    st.subheader(f"「 {q['word']} ] の意味は？")

    # 出題された瞬間に音声を自動再生
    if st.session_state.en_play_audio:
        audio_data = get_audio(q['word'])
        st.audio(audio_data, format="audio/mp3", autoplay=True)
        st.session_state.en_play_audio = False

    # 選択肢ボタン（5択）
    for opt in st.session_state.en_current_options:
        if st.button(opt, key=f"btn_{st.session_state.en_round}_{len(st.session_state.en_queue)}_{opt}"):
            if opt == q['meaning']:
                st.session_state.en_mastered_count += 1
                move_to_next()
                st.rerun()
            else:
                st.session_state.en_wrong_list.append(q)
                st.session_state.en_step = 'feedback_wrong'
                st.rerun()
