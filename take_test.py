import streamlit as st
import json
import openai


def app():
    st.title("Take Test Page")

    # Upload the generated test JSON file from the sidebar.
    test_file = st.sidebar.file_uploader("Upload Generated Test JSON file", type=["json"])
    if test_file is not None:
        try:
            test_json = json.load(test_file)
        except Exception as e:
            st.error(f"Error loading test JSON file: {e}")
            test_json = None
    else:
        st.error("Please upload your Generated Test JSON file.")
        test_json = None

    # Retrieve the API key from session state.
    api_key = st.session_state.get("openai_key")
    if not api_key:
        st.error("Please enter your OpenAI API key in the main sidebar to continue.")
        return

    openai.api_key = api_key

    if test_json is not None:
        questions = test_json.get("questions", [])
        if not questions:
            st.error("No questions found in the test JSON.")
        else:
            st.header("Take Your Test")
            user_answers = {}
            with st.form("test_form"):
                for idx, q in enumerate(questions):
                    q_type = q.get("type", "multiple_choice")
                    question_text = str(q.get("question", ""))
                    st.markdown(f"**Question {idx + 1}:** {question_text}")

                    if q_type == "multiple_choice":
                        options = q.get("options", {})
                        st.markdown(f"*A:* {str(options.get('A', ''))}")
                        st.markdown(f"*B:* {str(options.get('B', ''))}")
                        st.markdown(f"*C:* {str(options.get('C', ''))}")
                        st.markdown(f"*D:* {str(options.get('D', ''))}")
                        answer = st.radio(f"Your answer for Q{idx + 1}", ["A", "B", "C", "D"], key=f"q_{idx}")
                        user_answers[idx] = answer
                    elif q_type in ["short_answer", "code"]:
                        user_answers[idx] = st.text_area(f"Your answer for Q{idx + 1}", key=f"q_{idx}", height=80)
                    else:
                        st.error(f"Unknown question type: {q_type}")
                submitted = st.form_submit_button("Submit Test")

            if submitted:
                with st.spinner("Grading your test..."):
                    total_q = len(questions)
                    grading_prompt = (
                        f"Grade the following test with {total_q} questions. For each question, provide a detailed breakdown including:\n"
                        "1. The correct answer.\n"
                        "2. The student's answer.\n"
                        "3. A score for the question (e.g., 0/1, 1/1, or 0.5/1).\n"
                        "4. A brief comment on what the student did well and what they need to improve.\n\n"
                        "Format your answer as follows:\n"
                        "Here are the grades for each question:\n\n"
                        "Question 1: Correct Answer: <...> Student Answer: <...> Grade: <.../...>\n"
                        "Question 2: Correct Answer: <...> Student Answer: <...> Grade: <.../...>\n"
                        "...\n"
                        "Total Grade: <.../...>\n\n"
                        "Then, provide overall recommendations for improvement.\n\n"
                    )

                    for idx, q in enumerate(questions):
                        question_text = str(q.get("question", ""))
                        correct_answer = str(q.get("answerKey", "")).strip()
                        student_answer = str(user_answers.get(idx, "")).strip()
                        grading_prompt += (
                            f"Question {idx + 1}: {question_text}\n"
                            f"Correct Answer: {correct_answer}\n"
                            f"Student Answer: {student_answer}\n\n"
                        )

                    try:
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system",
                                 "content": "You are an exam grader that provides detailed feedback."},
                                {"role": "user", "content": grading_prompt}
                            ],
                            temperature=0.7
                        )
                        grading_result = response.choices[0].message.content
                        st.subheader("Grading Results:")
                        st.write(grading_result)
                    except Exception as e:
                        st.error(f"Error during grading: {e}")
