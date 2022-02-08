import socket
from datetime import datetime

from dotenv import dotenv_values
from emoji import demojize
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

class QuestionMan:
    sock = None
    id: str
    drive = None
    MIME = 'application/vnd.google-apps.document'

    def __init__(self) -> None:
        # var init block

        server = 'irc.chat.twitch.tv'
        port = 6667
        self.sock = socket.socket()
        config = dotenv_values("./.env")
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
        # gauth setup
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(gauth)

        # google file setup
        search_request = {'q': "title='" + config['DRIVE_FILE_NAME'] + "' and trashed=false"}
        file_list = self.drive.ListFile(search_request).GetList()
        if not len(file_list):
            file = self.drive.CreateFile({
                'title': config['DRIVE_FILE_NAME'],
                'mimeType': self.MIME,
            })
            file.Upload(param={'convert': True})
            file_list = self.drive.ListFile(search_request).GetList()
        self.id = file_list[0]['id']

        # twitch connect block
        self.sock.connect((server, port))
        self.sock.send(("PASS " + config['TOKEN'] + "\n").encode('utf-8'))
        self.sock.send(("NICK " + config['USER'] + "\n").encode('utf-8'))
        self.sock.send(("JOIN #" + config['CHANNEL'] + "\n").encode('utf-8'))

        # lets see if this works
        self.sock.recv(2048).decode('utf-8')

        while True:
            resp = self.sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))
            
            elif len(resp) > 0:
                text_parts = demojize(resp)[1:].split(":", 1)
                chat_name = text_parts[0].split('!')[0]
                print(chat_name + ": " + text_parts[1][:-1])
                if text_parts[1].startswith('!q ') or text_parts[1].startswith('!Q '):
                    self.send_block(chat_name +" at " + str(datetime.now()) + "\n" + text_parts[1][3:])
    
    def send_block(self, str_block: str):
        file = self.drive.CreateFile({'id': self.id})
        content: str = file.GetContentString(mimetype="text/plain", remove_bom=True)
        file.SetContentString(content.rstrip("\n") + "\n\n" + str_block + "\n")
        file.Upload()
    
    def __del__(self):
        self.sock.close()


QuestionMan()
