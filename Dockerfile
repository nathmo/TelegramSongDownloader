FROM alpine:latest
ADD TelegramMusic.py /
RUN apk update && \
    apk upgrade && \
    apk add python3
    apk add ffmpeg
    apk add py3-pip
RUN pip3 install -r requirements.txt
ENV SFTPPASSWORD=""
ENV SFTPUSERNAME=""
ENV SFTPHOST=""
ENV SFTPREMOTEBASEPATH=""
ENV TELEGRAMID=""
ENV TELEGRAMBOTTOKEN=""
CMD [ "python", "./TelegramMusic.py" ]
