# Use the official Python base image
FROM python:3.10.2-slim

WORKDIR /app

COPY . . 

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt --verbose

CMD ["streamlit", "run", "app.py"]