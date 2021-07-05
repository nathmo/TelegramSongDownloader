"""
Work over telegram.
either send a link and receive posible name for the track
or send a commend to edit the traswords database
or review the trashword database
or delete an entry in the trashword database

TODO : Allow parrallel download
"""


import pysftp
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import youtube_dl
from youtube_dl import YoutubeDL
import os
import editdistance
import eyed3
import sys

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class scope():
    def __init__(self, SFTPPASSWORD, SFTPUSERNAME, HOST, PORT, SFTPREMOTEBASEPATH, TELEGRAMID, TELEGRAMBOTTOKEN):
        self.STATE = 0
        self.video_metadata = {}
        self.SFTPPASSWORD = SFTPPASSWORD
        self.SFTPUSERNAME = SFTPUSERNAME
        self.HOST = HOST
        self.PORT = PORT
        self.SFTPREMOTEBASEPATH = SFTPREMOTEBASEPATH
        self.TELEGRAMID = TELEGRAMID
        self.TELEGRAMBOTTOKEN = TELEGRAMBOTTOKEN

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
        if str(update.message.chat_id) is self.TELEGRAMID:  # allow only a specific set of user to issue command
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
        # extracting song title
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
        # Preparing Path
        basepath_artist = os.path.join(self.SFTPREMOTEBASEPATH, artist)
        path_and_mp3_filename = os.path.join(basepath_artist, artist + " - " + song + ".mp3")
        mp3_filename = artist + " - " + song + ".mp3"
        mp4_filename = artist + " - " + song + ".mp4"
        #Downloading video
        youtube_dl_opts = \
            {

                'format': 'bestaudio/best',
                'postprocessors':
                    [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',
                    }],
                'outtmpl': mp4_filename
            }
        with YoutubeDL(youtube_dl_opts) as ydl:
            info_dict = ydl.extract_info(video_metadata["url"], download=False)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)
            ydl.download([video_metadata["url"]]) # the video is downloaded as mp4 by youtube-dl, converted to mp3
            print(video_title) # then the mp4 is automatically deleted
            print(video_id)

        print(artist)
        print(song)
        print(video_metadata["url"])
        #adding metadata
        try:
            audiofile = eyed3.load(mp3_filename)

            audiofile.tag.artist = artist
            audiofile.tag.title = song
            audiofile.tag.url = video_metadata["url"]
            audiofile.tag.save()
        except Exception as e:
            print(e)
            print("metadata couldnt be updated...")

        # Copying the file to the server
        print("moving " + mp3_filename + " to " + path_and_mp3_filename)
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            srv = pysftp.Connection(host=self.HOST, port=self.PORT, username=self.SFTPUSERNAME, password=self.SFTPPASSWORD, cnopts=cnopts)
            print("Connected to Host")
            try:
                with srv.cd(self.SFTPREMOTEBASEPATH):  # chdir to music folder
                    print("Retrieving music folder")
                    if not srv.exists(basepath_artist): # check if artist aldready have folder and create it if needed
                        try:
                            srv.makedirs(basepath_artist)
                        except Exception as e:
                            print(e)
                            print("Creation of the directory %s failed" % basepath_artist)
                try:
                    with srv.cd(basepath_artist):  # chdir to the artist folder
                        srv.put(mp3_filename, confirm=True)  # upload file (confirm the size) # this function is blocking
                except:
                    update.message.reply_text(artist + " - " + song + " aldready exist !")
                os.remove(mp3_filename) # otherwise the file might be deleted before the upload end
            finally:
                # Closes the connection
                srv.close()

        except Exception as e:
            print(e)
            print("error in SFTP connection")

        update.message.reply_text(artist + " " + song + " added !")

    def getPossibleTrackMetadata(self, videoTitle):

        # remove useless word from video title
        word_blob = list(videoTitle.split(" "))
        word_blob2 = []
        for word in word_blob:
            word = word.replace('"', "")  # This filtering method is durty and requier imprivement for case like ft. XXX
            word = word.replace("'", "")
            word = word.replace("'", "")
            word = word.replace("]", "")
            word = word.replace("[", "")
            word = word.replace("(", "")
            word = word.replace(")", "")
            word_blob2.append(word)

        word_blob = word_blob2
        
        for word in word_blob:
            for trashword in self.load_trashword():
                if editdistance.eval(word.lower(), trashword.lower()) <= 1:
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

        # generate possible track name
        possible_file_name = []
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
        print(self.TELEGRAMID)
        if str(update.message.chat_id) == self.TELEGRAMID:  # allow only a specific set of user to issue command
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
        else:
            print("User not in whitelist")

    def is_supported(self, url):
        extractors = youtube_dl.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME != 'generic':
                return True
        return False


def main():
    try :
        SFTPPASSWORD = os.environ['SFTPPASSWORD']
        SFTPUSERNAME = os.environ['SFTPUSERNAME']
        HOST = os.environ['SFTPHOST']
        PORT = os.environ['SFTPPORT']
        SFTPREMOTEBASEPATH = os.environ['SFTPREMOTEBASEPATH']
        TELEGRAMID = os.environ['TELEGRAMID']
        TELEGRAMBOTTOKEN = os.environ['TELEGRAMBOTTOKEN']
    except:
        try:
            HOST = sys.argv[1]
            PORT = sys.argv[2]
            SFTPUSERNAME = sys.argv[3]
            SFTPPASSWORD = sys.argv[4]
            SFTPREMOTEBASEPATH = sys.argv[5]
            TELEGRAMID = sys.argv[6]
            TELEGRAMBOTTOKEN = sys.argv[7]
        except:
            print("Either set the env variable or provided the argument to the command line")
            print("You MUST use the following order for the command line argument")
            print("TelegramMusic.py 102.168.1.10 nemo superSecureSFTPPassword /path/to/the/remote/music/folder telegramIDOftheUser TelegramBotToken")
            print("otherwise use the followings ENV variable : ")
            print("SFTPPASSWORD")
            print("SFTPUSERNAME")
            print("SFTPHOST")
            print("SFTPPORT")
            print("SFTPREMOTEBASEPATH")
            print("TELEGRAMID")
            print("TELEGRAMBOTTOKEN")

    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TELEGRAMBOTTOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    sc = scope(SFTPPASSWORD, SFTPUSERNAME, HOST, PORT, SFTPREMOTEBASEPATH, TELEGRAMID, TELEGRAMBOTTOKEN)
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