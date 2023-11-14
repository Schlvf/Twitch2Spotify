FROM python:3.11.6-slim-bullseye
EXPOSE 8000

WORKDIR /

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python","main.py"]
