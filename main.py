import json
import streamlit as st
import time
from datetime import datetime


class ChatGUI():

    with open('config/bot.json', 'r', encoding='utf-8') as f:
        BOT_CONFIG = json.load(f)

    with open('config/prompts.json', 'r', encoding='utf-8') as f:
        PROMPTS = json.load(f)

    date = datetime.now().strftime("%d/%m/%Y")

    def __init__(self) -> None:

        self._init_session_state()
        self._init_sidebar()
        self._init_chatui()

    def _init_session_state(self) -> None:
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": self.PROMPTS['init']}]

    def _init_sidebar(self) -> None:
        self.openai_api_key = st.sidebar.text_input(
            label='Nhập OpenAI API Key của bạn:',
            value=self.BOT_CONFIG['openai_api_key'],
            key='chatbot_api_key',
            type='password')

        self.save_bot_config = st.sidebar.button(label='Lưu cấu hình', use_container_width=True)

        if self.save_bot_config:
            self.BOT_CONFIG['openai_api_key'] = self.openai_api_key
            with open('config/bot.json', 'w', encoding='utf-8') as f:
                json.dump(self.BOT_CONFIG, f, ensure_ascii=False, indent=4)
            st.success('Đã lưu cấu hình thành công')

    def _init_chatui(self) -> None:
        st.title("💬TTChat - Cùng mua laptop nhé")
        st.caption(f"🚀 Dữ liệu về laptop được cập nhật đến ngày {self.date}")

        if not self.openai_api_key:
            st.info("Vui lòng nhập OpenAI API Key để tiếp tục")
            st.stop()

        # Load message history of session into chat message
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

    def _type_writer(self) -> None:
        pass


if __name__ == '__main__':
    chat = ChatGUI()
