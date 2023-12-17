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
from src.utils.csv_builder import create_temp_csv_file
from src.utils.chat_on_demand import chat_on_demand
from src.utils.load_prompts import load_prompts
from src.utils.google_sheet import read_data, update_data

if 'current_query' not in st.session_state:
    st.session_state['current_query'] = None

if 'remain_laptops' not in st.session_state:
    st.session_state['remain_laptops'] = None

if 'current_laptops' not in st.session_state:
    st.session_state['current_laptops'] = None

if 'show_form' not in st.session_state:
    st.session_state['show_form'] = False


def _submit_user_data():
    # Get all data in sidebar
    data = {}

    # Get the last ID
    data['STT'] = read_data().iloc[-1]['STT'] + 1
    data['Họ và Tên'] = st.session_state.get('user_name', '')
    data['Số điện thoại'] = st.session_state.get('user_phone', '')
    data['Email'] = st.session_state.get('user_email', '')
    data['Ngày hẹn (Dự kiến)'] = st.session_state.get('user_date', '')
    data['Giờ hẹn (Dự kiến)'] = st.session_state.get('user_time', '')
    data['Lí do khách hàng hẹn'] = st.session_state.get('user_reason', '')

    for key, value in data.items():
        if value == '':
            st.error(f'Vui lòng điền đầy đủ thông tin vào {key}')
            return

    if not data['Ngày hẹn (Dự kiến)'] == '':
        data['Ngày hẹn (Dự kiến)'] = data['Ngày hẹn (Dự kiến)'].strftime("%d/%m/%Y")

    if not data['Giờ hẹn (Dự kiến)'] == '':
        data['Giờ hẹn (Dự kiến)'] = data['Giờ hẹn (Dự kiến)'].strftime("%H:%M")

    data['STT'] = int(data['STT'])

    print(data)

    with st.spinner('Đang viết dữ liệu vào Google Sheet ...'):
        # Update the data
        update_data(data)

    msg = 'Đã gửi thông tin thành công, em sẽ liên hệ với anh/chị trong thời gian sớm nhất !'
    st.session_state.messages.append(
        {'role': 'assistant', 'content': msg}
    )
    _type_writer(msg, speed=40)

    # Thank you for using the chatbot
    msg = 'Em cảm ơn anh/chị đã sử dụng dịch vụ tư vấn của em - TTChat ạ'
    st.session_state.messages.append(
        {'role': 'assistant', 'content': msg}
    )
    _type_writer(msg, speed=40)

    st.balloons()

    st.session_state['show_form'] = False


if st.session_state['show_form']:
    # Create in sidebar
    st.sidebar.subheader('Thông tin khách hàng')
    user_name = st.sidebar.text_input(label='Họ và tên', key='input_user_name')
    phone_num = st.sidebar.text_input(label='Số điện thoại', key='input_user_phone')
    email = st.sidebar.text_input(label='Email', key='input_user_email')
    meet_date = st.sidebar.date_input(label='Ngày hẹn (Dự kiến)', key='input_user_date')
    meet_time = st.sidebar.time_input(label='Giờ hẹn (Dự kiến)', key='input_user_time')
    reason = st.sidebar.text_input(label='Lí do khách hàng hẹn', key='input_user_reason')

    if user_name:
        st.session_state.user_name = user_name

    if phone_num:
        st.session_state.user_phone = phone_num

    if email:
        st.session_state.user_email = email

    if meet_date:
        st.session_state.user_date = meet_date

    if meet_time:
        st.session_state.user_time = meet_time

    if reason:
        st.session_state.user_reason = reason

    # Submit button
    submit = st.sidebar.button(label='Gửi thông tin', key='submit', on_click=_submit_user_data)


def current_context_calculator() -> int:
    text = ''
    for msg in st.session_state.messages:
        text += msg['content']

    tokens: int = (len(text) % 16000) // 4

    return tokens


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


sys.excepthook = my_exception_hook


def _type_writer(text: str, speed: int = 100) -> None:
    if text is None or text == '':
        return
    tokens = text
    container = st.empty()
    for index in range(len(tokens) + 1):
        curr_full_text = tokens[:index]
        container.markdown(curr_full_text)
        time.sleep(1 / speed)


def release_context_token() -> None:
    """
        This function will keep the last answer of the chatbot and user to release the context token.
    """
    if st.session_state.remain_laptops:

        # Continue get max 5 laptops
        header = st.session_state.remain_laptops.split('\n')[0]
        send_content = '\n'.join(st.session_state.remain_laptops.split('\n')[1:5])
        remain_content = '\n'.join(st.session_state.remain_laptops.split('\n')[5:])

        st.session_state.remain_laptops = header + '\n' + remain_content

        # Blank the message
        st.session_state.messages = []

        # Load system guide
        st.session_state.messages.append(
            {"role": "system", "content": load_prompts('system_guide_preview_query')}
        )
        st.session_state.conversation.append(
            {"role": "system", "content": load_prompts('system_guide_preview_query')}
        )

        st.session_state.messages.append(
            {"role": "system", "content": f'Đây là kết quả mới nhất gồm những laptop phù hợp với tiêu chí người dùng chọn ra. Hãy ghi nhớ nó để tư vấn thật nhiệt tình cho người dùng nhé\n {header}\n{send_content}'}
        )
        st.session_state.conversation.append(
            {"role": "system", "content": f'Đây là kết quả mới nhất gồm những laptop phù hợp với tiêu chí người dùng chọn ra. Hãy ghi nhớ nó để tư vấn thật nhiệt tình cho người dùng nhé\n {header}\n{send_content}'}
        )

    else:
        header = ''
        send_content = ''
        remain_content = ''

    # Keep last answer
    last_answer = st.session_state.messages[-1]

    # Add last answer
    st.session_state.messages.append(
        {"role": "system", "content": f'Đây là câu nói/ câu hỏi cuối cùng của người dùng. Hãy tiếp tục trả lời nó: {last_answer}'}
    )
    st.session_state.conversation.append(
        {"role": "system", "content": f'Đây là câu nói/ câu hỏi cuối cùng của người dùng. Hãy tiếp tục trả lời nó: {last_answer}'}
    )

    with st.spinner('Thinking ...'):
        message = chat_on_demand(
            messages=st.session_state.messages
        )

    _type_writer(message, speed=100)


def store_user_requirement(content: str) -> None:
    st.session_state['user_requirement'] = content


def get_laptop_detail(which_one: str):
    if st.session_state.current_laptops:
        # Get the second last message
        second_last_message = st.session_state.messages[-2]

        # Get the last message
        last_message = st.session_state.messages[-1]

        # Get the current laptop
        current_laptop = st.session_state.current_laptops

        with st.spinner('Thinking ...'):
            response = chat_on_demand(
                messages=[
                    second_last_message,
                    last_message,
                    {'role': 'system', 'content': f'Người dùng muốn xem thông tin chi tiết của máy đó: {which_one}, hãy trả lời dựa trên những chiếc laptop này nhé, nhớ là tìm kiếm xem người dùng muốn xem máy nào: {current_laptop}'},
                ]
            )

        st.session_state.messages.append(
            {'role': 'assistant', 'content': response}
        )
        st.session_state.conversation.append(
            {'role': 'assistant', 'content': response}
        )

        _type_writer(response, speed=100)


def discovery_more_laptop():
    if st.session_state.remain_laptops:
        # Get the second last message
        second_last_message = st.session_state.messages[-2]

        # Get the last message
        last_message = st.session_state.messages[-1]

        # Get the current laptop
        remain_laptops = st.session_state.remain_laptops

        with st.spinner('Thinking ...'):
            response = chat_on_demand(
                messages=[
                    second_last_message,
                    last_message,
                    {'role': 'system', 'content': f'Người dùng muốn xem thêm laptop, hãy trả lời dựa trên những chiếc laptop này nhé, nhớ là tìm kiếm dựa trên nhu cầu của người dùng: {st.session_state.user_requirement}. Laptop data is {remain_laptops}'},
                ]
            )

        st.session_state.messages.append(
            {'role': 'assistant', 'content': response}
        )
        st.session_state.conversation.append(
            {'role': 'assistant', 'content': response}
        )

        _type_writer(response, speed=100)
    else:
        st.session_state.messages.append(
            {'role': 'system', 'content': 'Hiện tại không còn laptop nào phù hợp với yêu cầu của người dùng nữa rồi, hãy tìm kiếm lại nhé'}
        )
        st.session_state.conversation.append(
            {'role': 'system', 'content': 'Hiện tại không còn laptop nào phù hợp với yêu cầu của người dùng nữa rồi, hãy tìm kiếm lại nhé'}
        )

        _type_writer('Hiện tại không còn laptop nào phù hợp với yêu cầu của người dùng nữa rồi, hãy tìm kiếm lại nhé', speed=100)


def queries_db(**kwargs):
    print('==========> Running queries_db function')

    # Calculate the current context, if it is greater than 85% of the total context, then release the context
    current_token = current_context_calculator()

    if current_token >= int(16000 * 85 / 100):
        # Release the context
        release_context_token()

    # First, release the current query and remain laptops
    st.session_state.current_query = None
    st.session_state.remain_laptops = None

    st.session_state.messages.append(
        {"role": "system", "content": "Người dùng đang muốn tìm kiếm laptop với các thông số như sau"}
    )

    # Next, store the user requirement
    store_user_requirement(kwargs.get('content', ''))

    max_retry = 5
    while max_retry > 0:
        conn = sqlite3.connect('database/ttchat.db')
        try:
            query = build_filter_query(**kwargs)

            with st.spinner('Thinking ...'):
                remind_query = chat_on_demand(messages=[
                    {"role": "system", "content": f"Bạn nhắc lại 1 chút về các tiêu chí bộ lọc mà bạn đã lựa chọn: {query} và giải thích vì sao bạn lại chọn nó cho người dùng hiểu. Sau khi giải thích xong, nhớ nói câu: Tiếp theo, mình sẽ tìm trên cơ sở dữ liệu từ những tiêu chí này"}
                ])

            st.session_state.messages.append(
                {"role": "system", "content": remind_query}
            )

            st.session_state.conversation.append(
                {"role": "system", "content": remind_query}
            )

            _type_writer(remind_query, speed=100)

            st.session_state.messages.append(
                {"role": "system", "content": f'Đang thực hiện truy vấn: {query}'}
            )
            st.session_state.conversation.append(
                {"role": "system", "content": f'Đang thực hiện truy vấn: {query}'}
            )
            print(f'==========> Query: {query}')
            query_result = conn.execute(query).fetchall()
        except Exception as e:
            print(traceback.format_exc())
            st.error('Đã xảy ra lỗi khi truy vấn CSDL, đang thử lại')
            max_retry -= 1
            time.sleep(1)
        else:
            conn.close()
            break

    if max_retry == 0:
        st.error('Đã xảy ra lỗi khi truy vấn CSDL, vui lòng khởi động lại')
        st.stop()

    # Now convert the query result to a csv file
    headers = ['id', 'product_name', 'url', 'present_price', 'old_price', 'discount', 'manufacturer', 'raw_html_path', 'laptop_type', 'cpu', 'cpu_generation', 'disk_type', 'disk_size', 'ram_gb',
               'max_ram_slot', 'screen_size', 'screen_resolution', 'screen_ratio', 'screen_refresh_rate', 'gpu_type', 'gpu_model', 'weight_kg', 'ports', 'special_features', 'release_year']

    filename = 'current_query.csv'

    csv_path = create_temp_csv_file(headers, query_result, filename)

    if not csv_path:
        st.error('Đã xảy ra lỗi khi tạo file csv, vui lòng thử lại')
        st.session_state.query_result = None
    else:
        st.session_state.query_result = csv_path

    if len(query_result) == 0:
        st.session_state.conversation.append(
            {"role": "assistant",
                "content": "Ui, hiện tại không có laptop nào phù hợp với yêu cầu của bạn rồi. Bạn có thể thay đổi cấu hình hoặc các thông số 1 chút (ví dụ như thay đổi mức giá, thay đổi dung lượng RAM, thay đổi dung lượng ổ cứng,...) để mình tìm kiếm lại nhé"}
        )

        st.chat_message("assistant").write(
            "Ui, hiện tại không có laptop nào phù hợp với yêu cầu của bạn rồi. Bạn có thể thay đổi cấu hình hoặc các thông số 1 chút (ví dụ như thay đổi mức giá, thay đổi dung lượng RAM, thay đổi dung lượng ổ cứng,...) để mình tìm kiếm lại nhé")
    else:
        st.session_state.messages.append(
            {"role": "assistant",
                "content": f"Đã tìm thấy {len(query_result)} laptop phù hợp với yêu cầu của bạn, trước tiên mình giới thiệu qua 5 mẫu laptop phù hợp nhất nhé"}
        )
        st.session_state.conversation.append(
            {"role": "assistant",
                "content": f"Đã tìm thấy {len(query_result)} laptop phù hợp với yêu cầu của bạn, trước tiên mình giới thiệu qua 5 mẫu laptop phù hợp nhất nhé"}
        )
        st.chat_message("assistant").write(
            f"Đã tìm thấy {len(query_result)} laptop phù hợp với yêu cầu của bạn, trước tiên mình giới thiệu qua 5 mẫu laptop phù hợp nhất nhé")

        # Now send the query result to the chatbot
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read().split('\n')

        # Just send the first 5 rows ~ 5 laptops. The remaining will be store in the session state
        header = csv_content[0]
        send_content = '\n'.join(csv_content[1:5])
        remain_content = '\n'.join(csv_content[5:])

        st.session_state.remain_laptops = header + '\n' + remain_content
        st.session_state.current_laptops = header + '\n' + send_content

        st.session_state.messages.append(
            {"role": "system", "content": f'Đây là kết quả mới nhất gồm những laptop phù hợp với tiêu chí người dùng chọn ra. Hãy ghi nhớ nó để tư vấn thật nhiệt tình cho người dùng nhé\n {st.session_state.current_laptops}'}
        )

        st.session_state.messages.append(
            {"role": "system", "content": load_prompts('system_guide_preview_query')}
        )
        with st.spinner('Thinking ...'):
            message = chat_on_demand(
                messages=st.session_state.messages
            )

        st.session_state.conversation.append(
            {"role": "assistant", "content": message}
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": message}
        )

        _type_writer(message, speed=100)


def buy_laptop_or_leave_contact():
    """
        This function is call when user want to contact with the human for some purpose (go to store, buy laptop, ...)
    Returns:
    """

    # Thank you for using the chatbot
    msg = 'Em cảm ơn anh/chị đã sử dụng dịch vụ của em, trước khi tiếp tục, em xin phép được hỏi anh/chị một số thông tin nhé'
    st.session_state.messages.append(
        {'role': 'assistant', 'content': msg}
    )
    _type_writer(msg, speed=40)

    _type_writer('Anh/chị điền giúp em những thông tin ở cột bên trái với ạ !', speed=40)

    st.session_state['show_form'] = True

    st.rerun()


class ChatGUI():

    with open('config/bot.json', 'r', encoding='utf-8') as f:
        BOT_CONFIG = json.load(f)

    with open('config/function_description.json', 'r', encoding='utf-8') as f:
        FUNCTION_DESCRIPTION = json.load(f)

    date = datetime.now().strftime("%d/%m/%Y")

    def __init__(self) -> None:

        self._init_session_state()
        self._init_sidebar()
        self._init_chatui()

        # Init OpenAI Client
        self.client = OpenAI(api_key=os.getenv('OPENAI'))

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

    def _init_session_state(self) -> None:
        if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "system", "content": load_prompts('system_init')},
                {"role": "assistant", "content": load_prompts('assistant_init')}
            ]

        if "conversation" not in st.session_state:
            st.session_state["conversation"] = [
                {"role": "system", "content": load_prompts('system_init')},
                {"role": "assistant", "content": load_prompts('assistant_init')}
            ]

    def _init_sidebar(self) -> None:
        pass

    def _init_chatui(self) -> None:
        st.title("💬TTChat - Cùng mua laptop nhé")
        st.caption(f"🚀 Dữ liệu về laptop được cập nhật đến ngày {self.date}")

        # Load message history of session into chat message
        for msg in st.session_state.conversation:
            if msg['role'] != 'system':
                st.chat_message(msg["role"]).write(msg["content"])

    def _refresh_role(self) -> None:
        current_token = current_context_calculator()

        print(f'Current tokens in context: {current_token}')

        if current_token >= int(16000 * 85 / 100):
            # Release the context
            release_context_token()

            st.session_state.messages.append(
                {'role': 'system', 'content': load_prompts('system_init')}
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
            if st.session_state.current_query:
                with open(st.session_state.current_query, 'r', encoding='utf-8') as f:
                    query = f.read()
                st.session_state.messages.append(
                    {"role": "system", "content": load_prompts('system_recal_current_query') + '\n' + query}
                )

            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.conversation.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            with st.spinner("Thinking..."):
                response = self._get_response()
                answer = response.choices[0].message

            if answer.function_call:
                _type_writer(f'Đang thực hiện hàm: {answer.function_call.name}')
                self.trigger_function(
                    status=True,
                    func_name=answer.function_call.name,
                    args=json.loads(answer.function_call.arguments)
                )
            else:
                _type_writer(answer.content)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response.choices[0].message.content})
                st.session_state.conversation.append(
                    {"role": "assistant", "content": response.choices[0].message.content})

            # Rerun to show the assistant's icon
            # st.rerun()

    # --------------------------- Function for trigger event --------------------------- #


if __name__ == '__main__':
    chat = ChatGUI()
