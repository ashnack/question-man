from typing import Optional, Any

from bs4 import BeautifulSoup
from configparser import ConfigParser
from requests import get


class CultMan:
    config: dict[str, str] = {}
    words: dict[str, Any] = {}

    HEADERS: dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
    }

    def init_bot(self, config) -> None:
        self.config = config
        parser = ConfigParser()
        parser.read('cult.ini')
        for word in parser.keys():
            if word != 'DEFAULT':
                for seperate in word.split('/'):
                    if seperate:
                        print('...' + seperate + " added to cult man")
                        self.words['!' + seperate] = parser[word]

    def read_chat(self, chat_name: str, text_parts: list[str]) -> Optional[str]:
        returns: Optional[None]
        for word, config in self.words.items():
            if text_parts[1].strip().lower() == word:
                config_dict = dict(config)
                return "PRIVMSG #" + self.config['CHANNEL'] + " : @" + chat_name + " : " + str(config['title']) + self.pull_page(config_dict)

    def pull_page(self, config) -> str:
        returns: str = ""
        if 'webpage' in config:
            page = get(config['webpage'], headers=self.HEADERS)
            if page.status_code != 200:
                print(page.text)
                raise ValueError('page was not retrieved')
            soup = BeautifulSoup(page.text, "html.parser")
            for elem in soup.select(config['query']):
                if returns:
                    returns += " - "
                else:
                    returns += " "
                returns += elem.text
        return returns

        
