FROM python:3.11.4

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 443

CMD ["streamlit", "run", "main.py", "--server.port", "443", "--server.address", "0.0.0.0"]
