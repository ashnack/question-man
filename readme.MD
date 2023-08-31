== Installation ==
- install python 3.8 or above
- download those files to a folder
- run install.bat in a command line window (shift right-click to make the open terminal window appear)
- rename .env.example as .env
- nename cult.ini.example as cult.ini (leave it empty if you don't need the feature)
- add the username of the twitch account to connect as a reader and get a token password here: https://twitchapps.com/tmi/
- get a client_secrets.json file in the way described below
  - follow the procedure here https://pythonhosted.org/PyDrive/quickstart.html#authentication and download the client secret. (stop after step 5)
  - rename the json file as client_secrets.json and drop it in this folder
  - go to https://console.developers.google.com/apis/credentials/consent and add the email you use with google drive to the test users.
  - run go.bat and a web browser window will open to ask you to log in. Log as the same user and continue when said that it's a test app

== Running ==
- This console window must run for the bot to work
- You can load it with windows and it will always work, even when you are not online.
- Anybody could run this bot, but the file ownership will be to the google account.
- To stop it, just close the terminal window it is running in.