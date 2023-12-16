import json
import traceback
import streamlit as st
import time
import sys
import os
import sqlite3
from datetime import datetime
from openai import OpenAI

from src.utils.gpt_trigger_function import build_filter_query, print_haha


def my_exception_hook(exctype, value, tb):
    formatted_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    os.makedirs("logs", exist_ok=True)

    with open("logs/error.log", "a", encoding='utf-8') as f:
        f.write(f"==>> Time: {formatted_time}\n")
        f.write(f"==>> Type: {exctype}\n")
        f.write(f"==>> Value: {value}\n")
        f.write("==>> Traceback:\n")
        traceback.print_tb(tb, file=f)
        f.write("\n")

    print(f"==>> Type: {type}")
    print(f"==>> Value: {value}")
    traceback.print_tb(tb)


def queries_db(**kwargs):
    print('==========> Running queries_db function')

    st.session_state.messages.append(
        {"role": "system", "content": "Người dùng đang muốn tìm kiếm laptop với các thông số như sau"}
    )

    query = build_filter_query(**kwargs)
    print(f'==========> Query: {query}')
    conn = sqlite3.connect('database/ttchat.db')
    query_result = conn.execute(query).fetchall()
    conn.commit()
    conn.close()

    # Now convert the query result to a csv file
    for x in query_result:
        print(x)

    st.session_state.messages.append(
        {"role": "system", "content": "Đã tìm thấy laptop phù hợp với yêu cầu của bạn"}
    )


sys.excepthook = my_exception_hook


class ChatGUI():

    with open('config/bot.json', 'r', encoding='utf-8') as f:
        BOT_CONFIG = json.load(f)

    with open('config/prompts.json', 'r', encoding='utf-8') as f:
        PROMPTS = json.load(f)

    with open('config/function_description.json', 'r', encoding='utf-8') as f:
        FUNCTION_DESCRIPTION = json.load(f)

    date = datetime.now().strftime("%d/%m/%Y")

    def __init__(self) -> None:

        self._init_session_state()
        self._init_sidebar()
        self._init_chatui()

        # Init OpenAI Client
        self.client = OpenAI(api_key=self.BOT_CONFIG['openai_api_key'])

        # Init message event
        self._message_event()

    def trigger_function(self, status: bool = False, func_name: str = '', args: dict = {}) -> None:
        """
        Trigger the function in the backend
        For example: if status is True, and func_name is queries_db
        then run queries_db(*args)
        Args:
            func_name (str): name of function
            args (dict): 
            {
                'arg1': value1,
                'arg2': value2,
            }
        """

        if status:
            if func_name in globals() and callable(globals()[func_name]):
                if args != {}:
                    globals()[func_name](**args)
                else:
                    globals()[func_name]()

    # --------------------------- Function for init --------------------------- #

    def _load_prompts(self, type: str) -> None:
        """
            Load path from json file and read the path (txt file) to get the prompt
        Args:
            type (str)

        Note that path must be start from root directory
        """
        path = self.PROMPTS[type]

        with open(f'prompts/{path}', 'r', encoding='utf-8') as f:
            prompt = f.read()

        return prompt.strip()

    def _init_session_state(self) -> None:
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "system", "content": self._load_prompts('system_init')},
                {"role": "assistant", "content": self._load_prompts('assistant_init')}
            ]

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
            if msg['role'] != 'system':
                st.chat_message(msg["role"]).write(msg["content"])

    def _refresh_role(self) -> None:
        text = ''
        for msg in st.session_state.messages:
            text += msg['content']

        tokens: int = (len(text) % 16000) // 4

        print(f'Current tokens in context: {tokens}')

        if tokens > 16000:
            st.session_state.messages.append(
                {'role': 'system', 'content': self._load_prompts('system_init')}
            )

            print('==========> Mission refreshed for chatbot to remember its role !')

    def _get_response(self) -> str:
        max_retry = 5

        while max_retry > 0:
            try:
                self._refresh_role()
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo-1106",
                    messages=st.session_state.messages,
                    timeout=30,
                    max_tokens=4096,
                    temperature=1,
                    function_call='auto',
                    functions=self.FUNCTION_DESCRIPTION
                )

                return response
            except Exception as e:
                print(traceback.format_exc())
                st.error('Đã xảy ra lỗi khi gửi request đến OpenAI, đang thử lại')
                max_retry -= 1
                time.sleep(2)

        if max_retry == 0:
            st.error('Đã xảy ra lỗi khi gửi request đến OpenAI, vui lòng khởi động lại')
            st.stop()

    def _message_event(self) -> None:
        if prompt := st.chat_input():
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            with st.spinner("Thinking..."):
                response = self._get_response()
                answer = response.choices[0].message

            if answer.function_call:
                self._type_writer(f'Đang thực hiện hàm: {answer.function_call.name}')
                self.trigger_function(
                    status=True,
                    func_name=answer.function_call.name,
                    args=json.loads(answer.function_call.arguments)
                )
            else:
                self._type_writer(answer.content)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.choices[0].message.content})

            # Rerun to show the assistant's icon
            # st.rerun()

    def _type_writer(self, text: str, speed: int = 100) -> None:
        if text is None or text == '':
            return
        tokens = text
        container = st.empty()
        for index in range(len(tokens) + 1):
            curr_full_text = tokens[:index]
            container.markdown(curr_full_text)
            time.sleep(1 / speed)

    # --------------------------- Function for trigger event --------------------------- #


if __name__ == '__main__':
    chat = ChatGUI()
