from datetime import datetime
from json.decoder import JSONDecodeError
import os
import re
import socket
import time

from dotenv import dotenv_values
from emoji import demojize
from pydrive2.auth import GoogleAuth, RefreshError
from pydrive2.drive import GoogleDrive


class QuestionMan:
    sock = None
    id: str
    drive = None
    MIME = 'application/vnd.google-apps.document'
    UNTAG = re.compile('<.*?>')
    config = dotenv_values("./.env")
    server = 'irc.chat.twitch.tv'
    port = 6667

    def __init__(self) -> None:
        print("""
                                    /%@@@@@@@@@@@@@@@@@@@@@@@@@%/
                            ,&@@@@@@@@@@@@@@@&&%##%&&&@@@@@@@@@@@@@@@@
                        %@@@@@@@@@#,@                           (@@@@@@@@@%
    *@@@@@@@@@@@@@@@@@@@@@%,        \                              ,%@@@@@@@@@@@@@@@@@@@@@@@/
    %@@@@@@@@@@@@@@@@@@%   @*          &#                              (@&&&&&&&&&@@&&@@&&@@@@/
    @@@@%           &/     @*    @@@     @@@@@@@@@@@@@@@@@&/          @/                 @@@@@@&,
    @@@@%           &/     @*   (@@@@     @&    *   @@@@@@@@@@@@&*   @                 /@@@@@@@@@@&
    @@@@%           &/     @*   (@@@@%    %&     ,/(@@@@@@@@@@@@@@@@@                 @@      %@@@@
    @@@@%           &*  #@@@*   #@@@     /@&    #@@,    (@@@@@@@@@@(                 @(      @@@@@
    @@@@%           &(@@@@@@*           &@@&    (@@,    (@@@@@@@@@                 /@      ,@@@@&
    @@@@%           &@@@@@@@@@@@@@@@@@@@@@@@####&@@(////%@@@@@@@%                 &&      /@@@@#
    #@@@@%           &@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@*                 @#      %@@@@
    #@@@@#%           &@@@@@@@@@@@@&           @@@@@@@@@@@@@@@@@                 #@,      @#@@@@#
(@@@@ /%           &@@@@@@@@@@@*             #@@@@@@@@@@@@@%                 @&      *@  *@@@@/
@@@@( /%           &@@@@@@@@@@                 @@@@@@@@@@@*                 @/      #@    /@@@@,
%@@@@  /%           &@@@@@@@@                    %@@@@@@@@                 /@       @(      @@@@%
,@@@@,  /%           &@@@@@@%                      *@@@@@#                 &&       @        ,@@@@,
#@@@@   /%           &@@@@@                          @@@,                ,@(      *@@*        @@@@(
&@@@&   /%           &@@@#                            %                 %@,      #@@@&        @@@@#
&@@@&   /%           &@@,           /@@@                               @&       &@@@@@        @@@@#
%@@@&   /%           &(            &(  %#                             @*       @@@@@@&        @@@@#
(@@@@   /%                       ,@     &*                          (@       *@@@@@@@*        @@@@(
@@@@/  /%                      %%      @@,                        @&       &@@@@@@@@        *@@@@
%@@@@  /%                     @,     /@@@@                      *@/       @@@@@@@@@*        @@@@#
@@@@% /%                   *@      @@@@@@%                    %@       ,@@@@@@@@@#        #@@@@
*@@@@*/%                  &#     ,@@@@@@@@#                  @%       #@@@@@@@@@/        /@@@@,
    /@@@@@%                ,@      #@@@@@@@@@@,               ,@,       @@@@@@@@@@         (@@@@*
    @@@@%               #%      @@@@@@@@@@@@@              #@        @@@@@@@@@#         %@@@@,
    @@@@@@%           @      *@@@@@@@@@@@@@@@            @%       *@@@@@@@@&          @@@@@
        &@@@%          /      @@@@@@@@@@@@@@@@@#         *@*       #@@@@@@@#          %@@@@#
        %@@@@@*       /   &@@@@@@@@@@@@@@@@@@@@@*       %@        &@@@@@#           /@@@@@
        *@@@@@#   /@       (@@@@@@@@@@@@@@@@@@@,     @#        @@@@/            #@@@@@,
            *@@@@@@,            *%@@@@@@@@@@@@@@@   *@,       (@*             ,@@@@@@,
                &@@@@@@                  /&@@@@@@@@% %@@       @%             @@@@@@%
                ,@@@@@@@(                        #@,  @     @,          #@@@@@@@
                    %@@@@@@@%*                        *@  ,@       *%@@@@@@@#
                        %@@@@@@@@@@*                   ##(%  /@@@@@@@@@@%
                            (@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
                                    ,(%@@@@@@@@@@@@@@@@@@@@##/,
""")
        # init
        drive = self.gauth()
        self.twitch_connect()

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

        while True:
            resp = self.get_message()

            if resp.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))
            
            elif len(resp) > 0:
                for text in resp.split('\n'):
                    if len(text) > 0:
                        text_parts = demojize(text)[1:].split(":", 1)
                        chat_name = text_parts[0].split('!')[0]
                        if len(text_parts) == 1:
                            print("Incorrect response: " + resp)
                        else:
                            print(chat_name + ": " + text_parts[1][:-1])
                            if text_parts[1].startswith('!q ') or text_parts[1].startswith('!Q '):
                                self.send_block("<p><b>" + chat_name + " at " + str(datetime.now())[:-7] + "</b></p><p>" + re.sub(self.UNTAG, '', text_parts[1][3:]) + "</p>")
                                if self.config.get('SHUT_UP_FEEDBACK', '') == '':
                                    self.sock.send(("PRIVMSG #" + self.config['CHANNEL'] + " : @" + chat_name + " : QuestionMan has received your question.\n").encode('utf-8'))
    
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

            content = content.replace('<p class="c1"><span class="c0"></span></p>', '')
            self.file.SetContentString(content[:-14] + "<p>" + str_block + "</p></body></html>")
            self.file.Upload()
        except RefreshError:
            self.please_refresh()

    def twitch_connect(self):
        self.sock = socket.socket()
        self.sock.connect((self.server, self.port))
        self.sock.send(("PASS " + self.config['TOKEN'] + "\n").encode('utf-8'))
        self.sock.send(("NICK " + self.config['USER'] + "\n").encode('utf-8'))
        self.sock.send(("JOIN #" + self.config['CHANNEL'] + "\n").encode('utf-8'))
        # test that everything is good
        self.get_message()
        self.sock.send(("PRIVMSG #" + self.config['CHANNEL'] + " : QuestionMan is reporting for duty.\n").encode('utf-8'))

    def get_message(self):
        try:
            return self.sock.recv(2048).decode('utf-8')
        except ConnectionResetError:
            self.sock.close()
            time.sleep(15)
            self.twitch_connect()
            return self.get_message()
    
    def __del__(self):
        if self.sock:
            self.sock.close()


QuestionMan()
