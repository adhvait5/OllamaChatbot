from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}

Answer:
"""

model = OllamaLLM(model = "mistral")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

if 'context' not in st.session_state:
    st.session_state.context = ""


def handle_conversation():

    title_css = """
        <style>
            .title {
                color: #FFFFFF;  /* Change this to your desired color */
            }
        </style>
    """

    st.markdown(title_css, unsafe_allow_html=True)
    st.sidebar.markdown('<h1 class="title">Welcome to Ollama!!</h1>', unsafe_allow_html=True)
    st.sidebar.markdown("Type 'exit' to clear my message.")

    #user_input = st.sidebar.text_input("Message Ollama: ", key="unique_user_input")

    with st.sidebar.form("my_form"):
        user_input = st.sidebar.text_input(
        "Ask me anything",
        "", key = "unique_user_input"
        )
        submitted = st.form_submit_button("Submit")

        if user_input:
            # Generate AI response
            with st.spinner('Wait for it...'):
                result = chain.invoke({"context": st.session_state.context, "question": user_input})
                # Display the AI response in a non-editable text area
                st.sidebar.text_area("Ollama:", result, key="ollama_response", height=400, disabled=True)

                # Update conversation context in session state
                st.session_state.context += f"\nUser: {user_input} \nAI: {result}"
        

if __name__ == "__main__":
    from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx

    # If not already running under Streamlit (e.g. user ran `python main.py`), launch via streamlit run
    if get_script_run_ctx() is None:
        import sys
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", __file__] + sys.argv[1:]
        sys.exit(stcli.main())
    else:
        handle_conversation()


