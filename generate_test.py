import streamlit as st
import json
import openai

def app():
    st.title("JSON Configuration Generator")
    st.write("Paste a sample test or test overview below to generate a JSON configuration file for the Test Generation page.")

    sample_text = st.text_area("Enter sample test/test overview text", height=300)

    # Get the API key from session state.
    api_key = st.session_state.get("openai_key")
    if not api_key:
        st.error("Please enter your OpenAI API key in the main sidebar to continue.")
        return

    # Set the API key for the OpenAI library.
    openai.api_key = api_key

    if st.button("Generate Configuration JSON"):
        if not sample_text.strip():
            st.error("Please paste a sample test overview.")
        else:
            with st.spinner("Generating configuration JSON..."):
                prompt = (
                    "You are a test configuration generator. Based on the sample test overview provided below, "
                    "generate a JSON configuration file that can be used by a test generation system. "
                    "The JSON must have exactly the following keys: 'topics', 'generate_prompt', and 'grading_prompt'.\n\n"
                    "The 'topics' key should be a list of topics mentioned in the sample. \n"
                    "The 'generate_prompt' should be a prompt template that instructs an AI to generate a test. "
                    "It must include placeholders for {topics}, {num_questions}, {question_types}, and {study_context}.\n"
                    "The 'grading_prompt' should be a prompt template for grading tests, which includes a placeholder {total} for the total number of questions.\n\n"
                    "Return only the JSON object in valid JSON format with no additional text or markdown formatting.\n\n"
                    "Sample Test Overview:\n"
                    f"{sample_text}\n\n"
                    "JSON configuration:"
                )
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an expert in generating configuration files."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    generated_text = response.choices[0].message.content.strip()

                    if generated_text.startswith("```"):
                        generated_text = generated_text.split("```", 2)[1].strip()

                    try:
                        config_json = json.loads(generated_text)
                        st.success("Configuration JSON generated successfully!")
                        st.json(config_json)

                        json_str = json.dumps(config_json, indent=2)
                        st.download_button("Download Configuration JSON", json_str, file_name="config_generated.json",
                                           mime="application/json")
                    except Exception as parse_err:
                        st.error(f"Error parsing generated JSON: {parse_err}\n\nGenerated text:\n{generated_text}")
                except Exception as e:
                    st.error(f"Error generating configuration JSON: {e}")
