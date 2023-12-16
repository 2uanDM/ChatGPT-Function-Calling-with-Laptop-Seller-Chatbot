from openai import OpenAI
import streamlit as st
import time


def typewriter(text: str, speed: int):
    tokens = text
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = tokens[:index]
        container.markdown(curr_full_text)
        time.sleep(1 / speed)


with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Chatbot")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106", messages=st.session_state.messages)

    typewriter(text=response.choices[0].message.content, speed=100)

    st.session_state.messages.append(
        {"role": "assistant", "content": response.choices[0].message.content})

    # Rerun to show the assistant's icon
    st.experimental_rerun()
