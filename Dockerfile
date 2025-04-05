FROM python:3.13.2-bookworm
WORKDIR /

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE ${PORT}
CMD ["python","main.py"]
