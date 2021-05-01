"""
Work over telegram.
either send a link and receive posible name for the track
or send a commend to edit the traswords database
or review the trashword database
or delete an entry in the trashword database

TODO : File are saved at a defined location over sftp
TODO : Allow parrallel download
TODO : use ENV variable to pass SFTP credentials and telegram user
TODO : Improve trashword usage
"""


import pysftp
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import youtube_dl
from youtube_dl import YoutubeDL
import os
import editdistance
import eyed3
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
import sklearn
import shutil
import time

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

SFTPPASSWORD = "SecurePasswordPlease"
SFTPUSERNAME = "nathann"
HOST = "192.168.1.10"

class scope():
    whitelist = ["186683583"]
    basepath = "/mnt/music"

    def __init__(self):
        self.STATE = 0
        self.video_metadata = {}

    def add_trashword(self, update, context):
        """
        this function add a trashword to the list such that they are automatically removed from the possible
        song title (trashword example : lyrics, cover, etc)
        :param update:
        :param context:
        :return:
        """
        trashwords = self.load_trashword()
        with open("trashwords.txt", "a+") as file_object:
            i = 0
            for trashword in update.message.text.split(' '):
                if i > 0:
                    if trashword.lower() not in trashwords:
                        file_object.write(trashword.lower() + "\n")
                        update.message.reply_text('added : ' + trashword.lower())
                i = i + 1

    def show_trashword(self, update, context):
        """
        this function show all trashword from the list  (trashword example : lyrics, cover, etc)
        :param update:
        :param context:
        :return:
        """
        trashwords = self.load_trashword()
        reply = ""
        for word in trashwords:
            reply = reply + word + "\n"
        print(reply)
        print("test : " + str(set(list(reply))))
        if set(list(reply)) == set("\n") or set(list(reply)) == set():
            reply = "No trashword in the list. You can add some with /addtw lyrics"
        update.message.reply_text(reply)

    def del_trashword(self, update, context):
        """
        this function remove a trashword from the list such that they are no longer automatically removed from the possible
        song title (trashword example : lyrics, cover, etc)
        :param update:
        :param context:
        :return:
        """
        trashwords = self.load_trashword()
        with open("trashwords.txt", "w") as file_object:
            for word in trashwords:
                if word.lower() in update.message.text.split(' '):
                    update.message.reply_text('deleted : ' + word.lower())
                else:
                    file_object.write(word.lower() + "\n")

    def load_trashword(self):
        trashwords = []
        if os.path.isfile('trashwords.txt'):
            with open('trashwords.txt', 'r') as fd:
                for i in list(fd.read().split('\n')):
                    if i is not "":
                        trashwords.append(i)
        return trashwords

    def welcome(self, update, context):
        """
        this function return the welcome message with a list of command
        :param update:
        :param context:
        :return:
        """
        help_message = """
        this tool allow you to download the audio from a youtube video
        it then propose you some possible title or let you write it from scratch
        file in the metadata and save the mp3

        /deltw delete the specified trashword from the trashword list (word that must be removed from URL when figuring out possible song title)
        /addtw add a new trashword (EX : lyric
        /showtw show the trashword list
        video URL (just paste the URL)
        """
        print(str(update.message.chat_id))
        print(update.message.text)
        if str(update.message.chat_id) in self.whitelist:  # allow only a specific set of user to issue command
            update.message.reply_text(help_message)

    def download(self, update, context, video_metadata):
        """
        this piece of code download a video and convert it to mp3
        video_metadata is a dictionnary contaninigs :
        user_choice
        1
        2
        url
        :param update:
        :param context:
        :return:
        """

        if video_metadata["user_choice"] == "1":
            artist = video_metadata["1"].split("-")[0].strip()
            song = video_metadata["1"].split("-")[1].strip()
        elif video_metadata["user_choice"] == "2":
            # user supplied the full title
            artist = video_metadata["2"].split("-")[0].strip()
            song = video_metadata["2"].split("-")[1].strip()
        else:
            # user supplied the full title
            artist = video_metadata["user_choice"].split("-")[0].strip()
            song = video_metadata["user_choice"].split("-")[1].strip()

        basepath_artist = os.path.join(self.basepath, artist)
        path_and_mp3_filename = os.path.join(basepath_artist, artist + " - " + song + ".mp3")

        srv = pysftp.Connection(host=HOST, username=SFTPUSERNAME,
                                password=SFTPPASSWORD, log="./temp/pysftp.log")

        with srv.cd('public'):  # chdir to public
            srv.put('C:\Users\XXX\Dropbox\test.txt')  # upload file to nodejs/

        # Closes the connection
        srv.close()

        if not os.path.isdir(basepath_artist):
            try:
                os.mkdir(basepath_artist)
            except OSError:
                print("Creation of the directory %s failed" % basepath_artist)
        #   'outtmpl': path_and_mp3_filename,
        youtube_dl_opts = \
            {

                'format': 'bestaudio/best',
                'postprocessors':
                    [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
            }
        with YoutubeDL(youtube_dl_opts) as ydl:
            info_dict = ydl.extract_info(video_metadata["url"], download=False)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)
            ydl.download([video_metadata["url"]])
            print(video_title)
            print(video_id)
        # url is supported and can be downloaded
        # Create MP3File instance.
        print("moving " + video_title + "-" + video_id + ".mp3" + " to " + path_and_mp3_filename)
        auto_generated_path = ""
        for path in os.listdir():
            if os.path.isfile(path):
                if path.endswith(".mp3"):
                    auto_generated_path = path
        print(auto_generated_path)
        print(path_and_mp3_filename)

        print(artist)
        print(song)
        print(video_metadata["url"])
        try:
            time.sleep(1)
            audiofile = eyed3.load(auto_generated_path)
            audiofile.tag.artist = artist
            audiofile.tag.title = song
            audiofile.tag.url = video_metadata["url"]

            audiofile.tag.save()
        except:
            print("metadata couldnt be updated...")
        try:
            shutil.move(auto_generated_path, path_and_mp3_filename)
        except:
            update.message.reply_text(artist + " - " + song + " aldready exist !")
            os.remove(auto_generated_path)

        while not os.path.isfile(path_and_mp3_filename):
            i = 0  # wait for the file to be moved...

        # After the tags are edited, you must call the save method.
        update.message.reply_text(artist + " " + song + " added !")

    def getPossibleTrackMetadata(self, videoTitle):

        # remove useless word from video title
        word_blob = list(videoTitle.split(" "))
        for word in word_blob:
            for trashword in self.load_trashword():
                if editdistance.eval(word.lower(), trashword.lower()) < 1:
                    try:
                        word_blob.remove(word)
                    except:
                        print("aldready removed")
        print(word_blob)
        possible_title = ""
        possible_artist = ""
        dash_seen = False
        # reconstruct possible song and artist name
        if "-" in word_blob:
            for word in word_blob:
                if len(word) > 1:
                    if dash_seen:
                        possible_title = possible_title + " " + word
                        possible_title = possible_title.strip()
                    else:
                        possible_artist = possible_artist + " " + word
                        possible_artist = possible_artist.strip()
                else:
                    dash_seen = True
        else:  # no dash present. check known artist
            print("no dash present infering possible cutting point")
            i = 0
            for word in word_blob:
                if i < 2:
                    possible_title = possible_title + " " + word
                    possible_title = possible_title.strip()
                else:
                    possible_artist = possible_artist + " " + word
                    possible_artist = possible_artist.strip()
                i = i + 1

        # list all known artists
        subfolders = os.listdir(self.basepath)
        artists = []
        for folder in subfolders:
            if os.path.isdir(folder):
                artists.append(folder)

        # check if possible filename is from a known artists
        possible_file_name = []
        if possible_title in artists:  # in case the artist and track name are inverted
            possible_file_name.append(possible_title + " - " + possible_artist)
            possible_file_name.append(possible_artist + " - " + possible_title)
        else:
            possible_file_name.append(possible_artist + " - " + possible_title)
            possible_file_name.append(possible_title + " - " + possible_artist)

        return possible_file_name

    def url_or_help(self, update, context):
        """
        check that the user is on the whitelist
        check that the user supplied a valid URL
        otherwise display the help tab
        propose a set of title (check if artist exist aldready, remove useless word)
        ask for the title
        check that the music dont exist aldready
        if no artist exist create folder
        download the music
        fill metadata

        :param update:
        :param context:
        :return:
        """

        print(str(update.message.chat_id))
        if str(update.message.chat_id) in self.whitelist:  # allow only a specific set of user to issue command
            if self.STATE == 0:
                if self.is_supported(update.message.text):
                    youtube_dl_opts = {}
                    try:
                        with YoutubeDL(youtube_dl_opts) as ydl:
                            info_dict = ydl.extract_info(update.message.text, download=False)
                            video_url = info_dict.get("url", None)
                            video_id = info_dict.get("id", None)
                            video_title = info_dict.get('title', None)
                    except:
                        # check that youtube dl still works.
                        try:
                            with YoutubeDL(youtube_dl_opts) as ydl:
                                info_dict = ydl.extract_info("https://www.youtube.com/watch?v=BaW_jenozKc", download=False)
                                video_url = info_dict.get("url", None)
                                video_id = info_dict.get("id", None)
                                video_title = info_dict.get('title', None)
                                update.message.reply_text("this video is not available")
                        except:
                            print("update youtube DL")
                            update.message.reply_text("youtube DL need to be updated")
                        return

                    possible_file_name = self.getPossibleTrackMetadata(video_title)

                    selection_text = "enter 1 for : " + possible_file_name[0] + "\n" + "\n" + "enter 2 for : " + \
                                     possible_file_name[
                                         1] + "\n" + "\n" + "enter 'artist - song' if the proposition are not correct"
                    self.video_metadata["url"] = update.message.text
                    self.video_metadata["1"] = possible_file_name[0]
                    self.video_metadata["2"] = possible_file_name[1]
                    update.message.reply_text(selection_text)
                    self.STATE = 1
                    return
                else:
                    self.welcome(update, context)
            if self.STATE == 1:
                self.STATE = 2
                self.video_metadata["user_choice"] = update.message.text
                self.download(update, context, self.video_metadata)
                self.STATE = 0
            if self.STATE == 2:
                update.message.reply_text("The previous song is still downloading. please wait")
            print(update.message.text)

    def is_supported(self, url):
        extractors = youtube_dl.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME != 'generic':
                return True
        return False


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1315556556:AAGmAN6tE7UFERaSmyZkJfZolWZauHHHfSI", use_context=True)
    whitelist = ["186683583"] # allowed account to use this tool
    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    sc = scope()
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", sc.welcome))
    dp.add_handler(CommandHandler("deltw", sc.del_trashword))
    dp.add_handler(CommandHandler("addtw", sc.add_trashword))
    dp.add_handler(CommandHandler("showtw", sc.show_trashword))

    # on noncommand i.e message - echo the message on Telegram
    convo = MessageHandler(Filters.text & ~Filters.command, sc.url_or_help)

    dp.add_handler(convo)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()