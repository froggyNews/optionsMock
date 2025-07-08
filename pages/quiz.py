import streamlit as st
from utils import quiz as quiz_utils

st.header("Quiz")

if "quiz" not in st.session_state:
    q, idx = quiz_utils.ask_question()
    st.session_state.quiz = {"q": q, "idx": idx}

qdata = st.session_state.quiz
st.write(qdata["q"]["question"])
choice = st.radio("Answer", qdata["q"]["options"])
if st.button("Submit Answer"):
    correct = qdata["q"]["options"].index(choice) == qdata["q"]["answer"]
    quiz_utils.record_result(correct, qdata["q"]["topic"])
    st.write("Correct" if correct else "Incorrect")
    q, idx = quiz_utils.ask_question()
    st.session_state.quiz = {"q": q, "idx": idx}

score, total, *_ = quiz_utils.load_history()
st.write(f"Score: {score}/{total}")

