FROM python:3.11-slim

RUN groupadd -r blackkittenproxy && useradd -r -g blackkittenproxy blackkittenproxy

WORKDIR /app
COPY . /app

RUN mkdir -p /tmp/blackkittenproxy && chown -R blackkittenproxy:blackkittenproxy /tmp/blackkittenproxy

USER blackkittenproxy

EXPOSE 8881

ENTRYPOINT ["python", "src/main.py"]
