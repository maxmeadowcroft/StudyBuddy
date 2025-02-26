import streamlit as st
import generate_test
import test_generation
import take_test


def main():
    st.sidebar.title("Test App Navigation")

    # Ensure the OpenAI API key is input only once.
    if "openai_key" not in st.session_state:
        st.session_state["openai_key"] = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
    else:
        # Show the input again to allow changes if needed, but it updates the same key.
        st.sidebar.text_input("Enter your OpenAI API Key", type="password", key="openai_key")

    # Navigation: Choose which app to use.
    app_mode = st.sidebar.radio(
        "Choose the app mode:",
        ("Generate Test JSON", "Generate Sample Test", "Take Test")
    )

    if app_mode == "Generate Test JSON":
        generate_test.app()
    elif app_mode == "Generate Sample Test":
        test_generation.app()
    elif app_mode == "Take Test":
        take_test.app()


if __name__ == "__main__":
    main()
