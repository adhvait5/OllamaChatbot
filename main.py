from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st
import base64

#Ensured that base64_image is embedded correctly in the background-image URL.
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

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

    image_path = "llamaImage.png" 
    base64_image = get_base64_image(image_path)

    background_css = f"""
        <style>
            .stApp {{
                background-image: url("data:image/png;base64,{base64_image}");
                background-size: cover;
                
                background-repeat: no-repeat;
            }}
        </style>
    """
    title_css = """
        <style>
            .title {
                color: #FFFFFF;  /* Change this to your desired color */
            }
        </style>
    """
    
    st.markdown(background_css, unsafe_allow_html=True)
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
    handle_conversation()


