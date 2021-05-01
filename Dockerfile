FROM python:3
ADD TelegramMusic.py /
RUN pip3 install -r requirements.txt
ENV SFTPPASSWORD=""
ENV SFTPUSERNAME=""
ENV SFTPHOST=""
ENV SFTPREMOTEBASEPATH=""
ENV TELEGRAMID=""
ENV TELEGRAMBOTTOKEN=""
CMD [ "python", "./TelegramMusic.py" ]
