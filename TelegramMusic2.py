"""
Work over telegram.
either send a link and receive posible name for the track
or send a commend to edit the traswords database
or review the trashword database
or delete an entry in the trashword database

File are saved at a defined location over sftp

Allow parrallel download

Test module work and requier update

"""


import pysftp

srv = pysftp.Connection(host="www.destination.com", username="root",
password="password",log="./temp/pysftp.log")

with srv.cd('public'): #chdir to public
    srv.put('C:\Users\XXX\Dropbox\test.txt') #upload file to nodejs/

# Closes the connection
srv.close()