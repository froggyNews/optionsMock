import streamlit as st
from utils import quiz as quiz_utils

st.header("Quiz")

difficulty = st.session_state.get("difficulty")

if "quiz" not in st.session_state:
    q, idx = quiz_utils.ask_question(difficulty=difficulty)
    st.session_state.quiz = {"q": q["question"], "opts": q["options"], "ans": q["answer"], "idx": idx, "topic": q.get("topic")}

qdata = st.session_state.quiz
st.write(qdata["q"])
choice = st.radio("Answer", qdata["opts"])
if st.button("Submit Answer"):
    correct = qdata["opts"].index(choice) == qdata["ans"]
    quiz_utils.record_result(correct, qdata.get("topic"))
    st.write("Correct" if correct else "Incorrect")
    q, idx = quiz_utils.ask_question(difficulty=difficulty)
    st.session_state.quiz = {
        "q": q["question"],
        "opts": q["options"],
        "ans": q["answer"],
        "idx": idx,
        "topic": q.get("topic"),
    }

score, total = quiz_utils.load_history()
st.write(f"Score: {score}/{total}")

