FROM alpine:latest
ADD TelegramMusic.py /
ADD requirements.txt /
ADD trashwords.txt /
RUN apk update
RUN apk upgrade
RUN apk add gcc
RUN apk add make
RUN apk add musl-dev
RUN apk add cargo
RUN apk add linux-headers
RUN apk add libc-dev
RUN apk add libffi-dev
RUN apk add openssl-dev
RUN apk add python3
RUN apk add python3-dev
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
