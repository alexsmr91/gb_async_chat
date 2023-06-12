FROM python:3.7.2-alpine3.8
RUN apk update && apk upgrade
COPY . ./chat-server
RUN pip install --upgrade pip && pip install -r ./chat-server/requirements.txt
CMD ["python", "./chat-server/server.py"]
