FROM alpine:latest
ADD TelegramMusic.py /
ADD requirements.txt /
ADD trashwords.txt /
RUN apk update
RUN apk upgrade
RUN apk add python3
RUN apk add ffmpeg
RUN apk add py3-pip
RUN pip3 install -r requirements.txt
ENV SFTPPASSWORD=""
ENV SFTPUSERNAME=""
ENV SFTPHOST=""
ENV SFTPREMOTEBASEPATH=""
ENV TELEGRAMID=""
ENV TELEGRAMBOTTOKEN=""
CMD [ "python", "./TelegramMusic.py" ]
