FROM node:lts-bookworm-slim AS build-stage

WORKDIR /build

COPY package*.json .
RUN npm install

COPY /static ./static
RUN npm run build

FROM python:3.13.2-slim-bookworm AS python-runtime

WORKDIR /webapp

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY /src/. .
COPY --from=build-stage /build/dist ./dist

CMD ["python","main.py"]
