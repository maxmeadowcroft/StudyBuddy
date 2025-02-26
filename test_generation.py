import streamlit as st
import json
import openai

def app():
    st.title("Test Generation Page")

    # Upload config JSON file from the sidebar.
    config_file = st.sidebar.file_uploader("Upload JSON configuration file", type=["json"])
    if config_file is not None:
        try:
            config = json.load(config_file)
        except Exception as e:
            st.error(f"Error loading JSON config: {e}")
            config = None
    else:
        st.error("Please upload your JSON configuration file.")
        config = None

    # Get the API key from session state.
    api_key = st.session_state.get("openai_key")
    if not api_key:
        st.error("Please enter your OpenAI API key in the main sidebar to continue.")
        return

    openai.api_key = api_key

    if config is not None:
        st.header("Generate a Custom Test")

        topics_list = config.get("topics", [])
        if topics_list:
            topics_options = topics_list + ["All of the Above"]
            chosen_topic_raw = st.selectbox("Select a Topic", topics_options)
            chosen_topic = ", ".join(topics_list) if chosen_topic_raw == "All of the Above" else chosen_topic_raw
        else:
            chosen_topic = st.text_input("Enter a Topic", value="Computer Security")

        q_types = st.multiselect("Select Question Types", ["Multiple Choice", "Short Answer", "Code"],
                                 default=["Multiple Choice"])
        type_map = {"Multiple Choice": "multiple_choice", "Short Answer": "short_answer", "Code": "code"}
        selected_types = [type_map[t] for t in q_types]

        num_questions = st.number_input("Number of Questions", min_value=1, max_value=50, value=5)
        study_context = st.text_area("Study Context (key points):",
                                     value=f"Cover key concepts related to {chosen_topic}")

        if st.button("Generate Test"):
            with st.spinner("Generating test via OpenAI..."):
                prompt_template = config.get(
                    "generate_prompt",
                    "Generate a custom test on {topics} with {num_questions} questions. Include only the following question types: {question_types}. Use the study context: {study_context}."
                )
                base_prompt = prompt_template.format(
                    topics=chosen_topic,
                    num_questions=num_questions,
                    study_context=study_context,
                    question_types=", ".join(selected_types)
                )

                question_format_parts = []
                if "multiple_choice" in selected_types:
                    question_format_parts.append(
                        '{"type": "multiple_choice", "question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "answerKey": "..."}'
                    )
                if "short_answer" in selected_types:
                    question_format_parts.append(
                        '{"type": "short_answer", "question": "...", "answerKey": "..."}'
                    )
                if "code" in selected_types:
                    question_format_parts.append(
                        '{"type": "code", "question": "...", "answerKey": "..."}'
                    )
                expected_format = "[\n  " + ",\n  ".join(question_format_parts) + "\n]"

                output_format = (
                    "Return only the JSON object in the following format without any additional text or markdown formatting:\n"
                    "{\"questions\": " + expected_format + "}"
                )

                prompt = base_prompt + "\n" + output_format

                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert test generator."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    generated_text = response.choices[0].message.content.strip()

                    if generated_text.startswith("```"):
                        generated_text = generated_text.split("```", 2)[1].strip()

                    try:
                        test_json = json.loads(generated_text)
                        if "questions" not in test_json:
                            st.error("Generated JSON does not contain a 'questions' key.")
                        else:
                            st.success("Test generated successfully!")
                            st.write("Generated Test JSON:")
                            st.json(test_json)

                            json_str = json.dumps(test_json, indent=2)
                            st.download_button("Download Test JSON", json_str, file_name="generated_test.json",
                                               mime="application/json")
                    except Exception as parse_err:
                        st.error(f"Error parsing JSON: {parse_err}\n\nGenerated text:\n{generated_text}")
                except Exception as e:
                    st.error(f"Error generating test: {e}")
