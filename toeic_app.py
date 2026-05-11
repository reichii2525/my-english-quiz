import streamlit as st
import pandas as pd
import random
from gtts import gTTS
import io

# --- ページ設定 ---
st.set_page_config(page_title="TOEIC英単語クイズ(日→英)", layout="centered")

# --- データと音声の準備 ---
def load_data():
    # ★ここが重要：TOEIC用のCSVを読み込むように指定しています
    df = pd.read_csv('toeic.csv').dropna(how='all')
    # スプレッドシートの列に合わせて A列:word, B列:meaning と仮定
    df.columns = ['word', 'meaning'] + list(df.columns[2:])
    return df.to_dict('records')

def get_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- 以下、クイズのプログラム本体（内容はreverse_app.pyと同じ） ---
if 'rev_words' not in st.session_state:
    st.session_state.rev_words = load_data()
    st.session_state.rev_total_count = len(st.session_state.rev_words)
    st.session_state.rev_queue = st.session_state.rev_words.copy()
    st.session_state.rev_wrong_list = []
    st.session_state.rev_mastered_count = 0
    st.session_state.rev_round = 1
    st.session_state.rev_current_q = None
    st.session_state.rev_step = 'ask'
    st.session_state.rev_prev_correct_word = None 

def move_to_next():
    if not st.session_state.rev_queue:
        st.session_state.rev_step = 'result'
        st.session_state.rev_current_q = None
    else:
        st.session_state.rev_current_q = st.session_state.rev_queue.pop(random.randrange(len(st.session_state.rev_queue)))
        q = st.session_state.rev_current_q
        all_words = [w['word'] for w in st.session_state.rev_words]
        wrong_opts = random.sample([w for w in all_words if w != q['word']], min(len(all_words)-1, 4))
        st.session_state.rev_current_options = random.sample(wrong_opts + [q['word']], len(wrong_opts) + 1)

if st.session_state.rev_current_q is None and st.session_state.rev_step != 'result':
    move_to_next()

st.title(f"TOEIC英単語クイズ Round {st.session_state.rev_round}")

if st.session_state.rev_step == 'result':
    accuracy = (st.session_state.rev_mastered_count / st.session_state.rev_total_count * 100) if st.session_state.rev_total_count > 0 else 0
    st.subheader(f"Round {st.session_state.rev_round} 終了")
    st.write(f"全 {st.session_state.rev_total_count} 問中、{st.session_state.rev_mastered_count} 問正解")
    st.metric("累計正答率", f"{accuracy:.1f}%")
    if not st.session_state.rev_wrong_list:
        st.balloons()
        st.success("🎉 全問マスター！お疲れ様でした！")
        if st.button("最初からやり直す"):
            st.session_state.clear()
            st.rerun()
    else:
        if st.button("次のラウンド（不正解分のみ）を開始"):
            st.session_state.rev_queue = st.session_state.rev_wrong_list.copy()
            st.session_state.rev_wrong_list = []
            st.session_state.rev_round += 1
            st.session_state.rev_step = 'ask'
            st.session_state.rev_prev_correct_word = None
            move_to_next()
            st.rerun()

elif st.session_state.rev_step == 'feedback_wrong':
    q = st.session_state.rev_current_q
    st.error(f"× 不正解！ 正解は： {q['word']}")
    if st.button("確認して次の問題へ", type="primary"):
        st.session_state.rev_prev_correct_word = None
        st.session_state.rev_step = 'ask'
        move_to_next()
        st.rerun()

elif st.session_state.rev_step == 'ask':
    if st.session_state.rev_prev_correct_word:
        st.success(f"〇 正解！ ({st.session_state.rev_prev_correct_word})")
        audio_data = get_audio(st.session_state.rev_prev_correct_word)
        st.audio(audio_data, format="audio/mp3", autoplay=True)
        st.session_state.rev_prev_correct_word = None

    q = st.session_state.rev_current_q
    st.subheader(f"「{q['meaning']}」に合う英単語は？")
    for opt in st.session_state.rev_current_options:
        if st.button(opt, key=f"btn_{st.session_state.rev_round}_{len(st.session_state.rev_queue)}_{opt}"):
            if opt == q['word']:
                st.session_state.rev_mastered_count += 1
                st.session_state.rev_prev_correct_word = q['word']
                move_to_next()
                st.rerun()
            else:
                st.session_state.rev_wrong_list.append(q)
                st.session_state.rev_step = 'feedback_wrong'
                st.rerun()
