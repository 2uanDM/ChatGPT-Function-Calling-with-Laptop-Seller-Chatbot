# ChatInnov-Hackathon-Bot

This repository keeps code for my hackathon competition in creating ChatGPT integrated chatbot named "TTChat", you can try it out in this url: http://34.124.191.129:443/

Here is the slides show the way we create this chatbot: [Link slide](https://husteduvn-my.sharepoint.com/:p:/g/personal/kiet_pt214909_sis_hust_edu_vn/EYEfEKZsKrlNoTWA-Pct0hIBvfSb4QeYiqMjngdn03zOgQ?e=LfAabK) 

GitHub url (With authentication key to private repo):

https://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@github.com/2uanDM/ChatInnov-Hackathon-Bot

## Installation

### Way 1: Using Pip

Step 1: Clone the repository

```bash
sudo git clone https://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@github.com/2uanDM/ChatInnov-Hackathon-Bot
```

Step 2: cd to the directory

```bash
cd ChatInnov-Hackathon-Bot
```

Step 3: Install requirements

```bash
sudo pip install -r requirements.txt
```

Step 4: Run the bot

```bash
sudo streamlit run main.py --server.port 443
```

Then you can access the GUI to chat with bot at:
http://34.124.191.129:443/

## Way 2: Using Docker

Step 1: Clone the repository

```bash
sudo git clone https://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@github.com/2uanDM/ChatInnov-Hackathon-Bot
```

Step 2: cd to the directory

```bash
cd ChatInnov-Hackathon-Bot
```

Step 3: Build the docker image

```bash
sudo docker build -t chatinnov .
```

Step 4: Run the docker image

```bash
sudo docker run -p 443:443 chatinnov
```

Then you can access the GUI to chat with bot at:

http://34.124.191.129:443/

## Note

In the provided server, I have clone the repo to path: /home/ChatInnov-Hackathon-Bot and also build the docker image with name: chatinnov

So you can directly run the docker image with command:

```bash
sudo docker run -p 443:443 chatinnov
```
