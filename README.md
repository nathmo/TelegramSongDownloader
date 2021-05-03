# TelegramSongDownloader
Telegram that download the song at the provided URL and upload it somewhere via SFTP
## Use Case
You have a NAS and you're not a big fan of not having a local copy of your music with you.
But manually downloading, renaming and filling metadata for your song is a tedious process
This tool does just that. It is still up to you to sync your music accross your device from your NAS
(in my cas the NAS is a RockPro64 with a bunch of harddrive running openmediavault, i use FolderSync on android to sync it and this app is hosted on a raspberry pi)

## Usage
Paste the link to the video you want to get the audio track
when promted give it a name (the program try to find the correct but in the case its wrong you can enter it manually)
wait and enjoy for your music to be send to the SFTP server (your NAS for instance)
![image](https://user-images.githubusercontent.com/15912256/116869015-2d09c000-ac10-11eb-9e81-2ba53bcca5ba.png)

## Normal Installation on debian like linux
### Cloning the repo
$ git clone https://github.com/nathmo/TelegramSongDownloader.git
$ cd TelegramSongDownloader
### Installings dependencies
$ sudo apt-get install python3, ffmpeg, python3-pip
$ pip3 install -r requirements.txt
### Running
$ python3 TelegramMusic.py SFTPHOST SFTPUSERNAME SFTPPASSWORD REMOTEPATHTOMUSICFOLDER CLIENTELEGRAMID BOTTELEGRAMID
(do not change the order of the value)
$ SFTPPASSWORD this is your ssh password
$ SFTPUSERNAME this is your ssh username
$ SFTPHOST this is the SFTP Host (any server with SSH enabled will do)
$ SFTPREMOTEBASEPATH replace this value with the absolute path where you want to store the song on your server
$ TELEGRAMID this is the telgram id of the account that will use this app. you can find it [there | https://www.technobezz.com/how-to-find-user-ids-in-telegram/]
$ TELEGRAMBOTTOKEN replace with the value you get using the [bot Father | https://www.telegram-group.com/en/blog/create-bot-telegram/]
## Docker Installation
### Cloning the repo
$ git clone https://github.com/nathmo/TelegramSongDownloader.git
$ cd TelegramSongDownloader
### Installings dependencies

$ curl -fsSL https://get.docker.com -o get-docker.sh
$ sudo sh get-docker.sh
$ sudo usermod -aG docker pi
$ docker volume create portainer_data
$ docker run -d -p 8000:8000 -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce

### Building the image
Edit the settings and fill the followings value : 

$ nano Dockerfile

$ SFTPPASSWORD="" this is your ssh password
$ SFTPUSERNAME="" this is your ssh username
$ SFTPHOST="" this is the SFTP Host (any server with SSH enabled will do)
$ SFTPREMOTEBASEPATH="" replace this value with the absolute path where you want to store the song on your server
$ TELEGRAMID="" this is the telgram id of the account that will use this app. you can find it [there | https://www.technobezz.com/how-to-find-user-ids-in-telegram/]
$ TELEGRAMBOTTOKEN="" replace with the value you get using the [bot Father | https://www.telegram-group.com/en/blog/create-bot-telegram/]

### Running
either lauch it using a docker command or connect to 127.0.0.1:9000 on the portainer interface and use that to execute the container
