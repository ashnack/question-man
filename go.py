from datetime import datetime
from glob import glob
from json.decoder import JSONDecodeError
import logging
import os
import re
import socket

from dotenv import dotenv_values
from emoji import demojize


class QuestionMan:
    sock = None
    id: str
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
        jobs_dir = os.path.join(os.getcwd(), 'jobs', '*.py')
        bot_list = []
        for file in glob(jobs_dir):
            file = file[len(jobs_dir)-4:-3]
            if file != '__init__':
                jobs_import = __import__('jobs.' + file)
                temp = getattr(getattr(jobs_import, file), file)()
                temp.init_bot(config=self.config)
                bot_list.append(temp)
                print(file + ' loaded')
        self.twitch_connect()

        while True:
            resp = self.get_message()

            if resp == False:
                return

            if resp.startswith('PING'):
                self.sock.send("PONG\n".encode('utf-8'))
            
            elif len(resp) > 0:
                for text in resp.split('\n'):
                    if len(text) > 0:
                        text_parts = demojize(text)[1:].split(":", 1)
                        chat_name = text_parts[0].split('!')[0]
                        if len(text_parts) == 1:
                            logging.error("Incorrect response: " + resp)
                        else:
                            print(chat_name + ": " + text_parts[1][:-1])
                            for bot in bot_list:
                                response = bot.read_chat(chat_name, text_parts)
                                if response and self.config.get('SHUT_UP_FEEDBACK', '') == '':
                                    self.sock.send((response + "\n").encode('utf-8'))

    def twitch_connect(self):
        self.sock = socket.socket()
        self.sock.connect((self.server, self.port))
        self.sock.send(("PASS " + self.config['TOKEN'] + "\n").encode('utf-8'))
        self.sock.send(("NICK " + self.config['USER'] + "\n").encode('utf-8'))
        self.sock.send(("JOIN #" + self.config['CHANNEL'] + "\n").encode('utf-8'))
        # test that everything is good
        self.get_message()
        if self.config.get('SHUT_UP_FEEDBACK', '') == '':
            self.sock.send(("PRIVMSG #" + self.config['CHANNEL'] + " : WilyBots are reporting for duty.\n").encode('utf-8'))

    def get_message(self):
        try:
            return self.sock.recv(2048).decode('utf-8')
        except KeyboardInterrupt:
            self.__del__()
            exit()
        except:
            return False

    def __del__(self):
        if self.sock:
            self.sock.close()

while True:
    QuestionMan()
