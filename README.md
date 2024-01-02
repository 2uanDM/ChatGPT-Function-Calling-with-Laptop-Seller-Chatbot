# Chat'Innov Hackathon - Laptop Seller Chatbot

This repository contains the code for the [Chat'Innov Hackathon](https://hust.edu.vn/vi/news/tin-tuc-su-kien/sinh-vien-dai-hoc-bach-khoa-ha-noi-thang-ap-dao-cuoc-thi-chat-innov-2023-654946.html) with the goal of creating a chatbot that can help a "poor" student to buy a best laptop with a limited budget. In this hackathon, we won the 1st prize and the gift is an Dell 💻 Inspiron 15 laptop 😊

This chatbot is created using:

- [Streamlit](https://www.streamlit.io/) framework for GUI

- [GPT-3.5-Turbo-16k](https://platform.openai.com/docs/models/gpt-3-5) model for the chatbot.

The interesting thing here is that the chatbot is guided using a SQLite database containing ~ 240 laptops crawled from [Thế Giới Di Động](https://www.thegioididong.com/) and using the new feature of ChatGPT API - [Function Calling](https://platform.openai.com/docs/guides/function-calling) to using some predefined functions.

![image](/images/home.png)

---

## Installation

- Clone this repository

```bash
git clone https://github.com/2uanDM/ChatGPT-Function-Calling-with-Laptop-Seller-Chatbot
```

- Change your environment variables in `.env` file

```
OPENAI="YOUR OPENAI API KEY"
TELEGRAM_ID="YOUR TELEGRAM ID"
TELEGRAM_BOT_TOKEN="YOUR BOT TOKEN"
```

### Way 1: Run directly on your machine

- Creating a virtual environment

```bash
# On Windows
python -m venv .venv

# On Linux
python3 -m venv .

# Conda users
conda create -n .venv python=3.11
```

- Activate the virtual environment

```bash
# On Windows
source .venv/Scripts/activate

# On Linux
source .venv/bin/activate

# Conda users
conda activate .venv
```

- Install the requirements

```bash
pip install -r requirements.txt
```

- Run the app

```bash
streamlit run main.py
```

### Way 2: Using Docker

- Build the image

```bash
docker build -t chatinnov .
```

- Run the container

```bash
docker run -p 443:443 chatinnov
```

(You can change the port to whatever you want)

---

## Repository Structure

| Name                 | Explain                                                                                                   | Location    |
| -------------------- | --------------------------------------------------------------------------------------------------------- | ----------- |
| [main.py](/main.py)  | The main file to run the app                                                                              | [~/]()      |
| [temp_queries]()     | The folder that contain temporary csv (query results when user asking chatbot for a specific laptop spec) | [~/.temp]() |
| [config](/config/)   | Folder that contain some configs for the app, including the function calling description                  | [~/]()      |
| [images](/images/)   | Folder that contain some images for the README.md                                                         | [~/]()      |
| [prompts](/prompts/) | Folder that contains some predefined prompts, acting as "system" in the GPT's API context                 | [~/]()      |
| [src](/src/)         | Folder that contains the source code for crawler                                                          | [~/]()      |
| [utils](/utils/)     | Folder that contains some utility functions                                                               | [~/]()      |

---
