import socket
from datetime import datetime

from dotenv import dotenv_values
from emoji import demojize
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class QuestionMan:
    sock = None

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
        drive = GoogleDrive(gauth)

        # google file setup
        file_list = drive.ListFile({'q': "title='" + config['DRIVE_FILE_NAME'] + "' and trashed=false"}).GetList()
        if len(file_list):
            id = file_list[0]['id']
            file = drive.CreateFile({'id': id})
        else:
            file = drive.CreateFile({'title': config['DRIVE_FILE_NAME'], 'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'})
            file.Upload(param={'convert': True})

        # twitch connect block
        self.sock.connect((server, port))
        self.sock.send(("PASS " + config['TOKEN'] + "\n").encode('utf-8'))
        self.sock.send(("NICK " + config['USER'] + "\n").encode('utf-8'))
        self.sock.send(("JOIN #" + config['CHANNEL'] + "\n").encode('utf-8'))

        # lets see if this works
        print(self.sock.recv(2048).decode('utf-8'))

        while True:
            resp = self.sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))
            
            elif len(resp) > 0:
                text_parts = demojize(resp)[1:].split(":", 1)
                chat_name = text_parts[0].split('!')[0]
                print(chat_name + ": " + text_parts[1][:-1])
                if text_parts[1].startswith('!q ') or text_parts[1].startswith('!Q '):
                    content = str(file.GetContentString())
                    file.SetContentString(content + "\n" + chat_name +" at " + str(datetime.now()) + "\n" + text_parts[1][3:] + "\n")
                    file.Upload()
    
    def __del__(self):
        self.sock.close()


QuestionMan()
