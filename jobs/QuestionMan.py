from datetime import datetime
from json.decoder import JSONDecodeError
import os
import re
import time

from pydrive2.auth import GoogleAuth, RefreshError
from pydrive2.drive import GoogleDrive


class QuestionMan:
    config = None
    drive = None
    MIME = 'application/vnd.google-apps.document'
    UNTAG = re.compile('<.*?>')

    def init_bot(self, config):
        drive = self.gauth()
        self.config = config

        # google file setup
        search_request = {'q': "title='" + self.config['DRIVE_FILE_NAME'] + "' and trashed=false"}
        file_list = drive.ListFile(search_request).GetList()
        if not len(file_list):
            file = drive.CreateFile({
                'title': self.config['DRIVE_FILE_NAME'],
                'mimeType': self.MIME,
            })
            file.Upload(param={'convert': True})
            file_list = drive.ListFile(search_request).GetList()
        id = file_list[0]['id']
        self.file = drive.CreateFile({'id': id})

    def gauth(self, in_loop=False):
        try:
            gauth = GoogleAuth()
            gauth.LocalWebserverAuth()
            return GoogleDrive(gauth)
        except RefreshError:
            if not in_loop:
                os.remove("credentials.json")
                return self.gauth(True)

    def please_refresh(self, msg="refresh needed"):
        self.sock.send(("PRIVMSG #" + self.config['CHANNEL'] + " : QuestionMan needs to be refreshed.\n").encode('utf-8'))
        print("please restart the application - " + msg)
        self.sock.close()
        exit()
    
    def send_block(self, str_block: str):
        try:
            self.file.content = None
            try:
                content: str = self.file.GetContentString(mimetype="text/html", remove_bom=True)
            except JSONDecodeError:
                time.sleep(1)
                try:
                    # let us retry before calling it quits
                    self.file.content = None
                    content: str = self.file.GetContentString(mimetype="text/html", remove_bom=True)
                except JSONDecodeError:
                    self.please_refresh("content coming in from the google doc seems invalid")
            if self.config.get('COLOR_OF_TEXT', ''):
                content = content.replace('<style type="text/css">', '<style type="text/css">body{background-color:' + self.config['COLOR_OF_BACKGROUND'] + ' !important;}span,p,hr{color:' + self.config['COLOR_OF_TEXT'] + ' !important;}')
            self.file.SetContentString(content[:-14] + "<hr><p>" + str_block + "</p></body></html>")
            self.file.Upload()
        except RefreshError:
            self.please_refresh()

    def read_chat(self, chat_name, text_parts):
        if text_parts[1].startswith('!q ') or text_parts[1].startswith('!Q '):
            self.send_block("<p><b>" + chat_name + " at " + str(datetime.now())[:-7] + "</b></p><p>" + re.sub(self.UNTAG, '', text_parts[1][3:]) + "</p>")
            return "PRIVMSG #" + self.config['CHANNEL'] + " : @" + chat_name + " : QuestionMan has received your question."
