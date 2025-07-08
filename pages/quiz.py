import streamlit as st
from utils import quiz as quiz_utils

st.header("Quiz")

if "quiz" not in st.session_state:
    q, opts, ans, idx = quiz_utils.ask_question()
    st.session_state.quiz = {"q": q, "opts": opts, "ans": ans, "idx": idx}

qdata = st.session_state.quiz
st.write(qdata["q"])
choice = st.radio("Answer", qdata["opts"])
if st.button("Submit Answer"):
    correct = qdata["opts"].index(choice) == qdata["ans"]
    quiz_utils.record_result(correct)
    st.write("Correct" if correct else "Incorrect")
    q, opts, ans, idx = quiz_utils.ask_question()
    st.session_state.quiz = {"q": q, "opts": opts, "ans": ans, "idx": idx}

score, total = quiz_utils.load_history()
st.write(f"Score: {score}/{total}")

