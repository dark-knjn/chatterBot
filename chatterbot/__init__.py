class ChatBot(object):

    def __init__(self, name="bot", logging=True):
        super(ChatBot, self).__init__()

        self.TIMESTAMP = self.timestamp()

        self.name = name
        self.log = logging
        self.log_directory = "conversation_engrams/"

    def timestamp(self, fmt="%Y-%m-%d-%H-%M-%S"):
        """
        Returns a string formatted timestamp of the current time.
        """
        import datetime
        return str(datetime.datetime.now().strftime(fmt))

    def update_log(self, data):
        import csv

        logtime = self.timestamp()
        logfile = open(self.log_directory + self.TIMESTAMP, "a")
        logwriter = csv.writer(logfile, delimiter=",")

        logwriter.writerow([
            data["user"]["name"],
            data["user"]["timestamp"],
            data["user"]["text"]
        ])

        for line in data["bot"]["text"]:
            if line: # Why 'if line?' This needs a comment or a fix.
                logwriter.writerow([
                    line.name,
                    line.date,
                    line.text
                ])

        logfile.close()

    def get_response_data(self, user_name, input_text):
        """
        Returns a dictionary containing the following data:
        * user:
            * The name of the user who instigated a response
            * The timestamp at which the user issued their statement
            * The user's statement
        * bot:
            * The name of the chat bot instance
            * The timestamp of the chat bot's response
            * The chat bot's response text
        """
        from chatterbot.engram import Engram

        # Check if a name was mentioned
        if self.name in input_text:
            pass

        bot = {}
        user = {}

        e = Engram()

        user["name"] = user_name
        user["text"] = input_text
        user["timestamp"] = self.timestamp()

        bot["name"] = self.name
        bot["text"] = e.engram(input_text, self.log_directory)
        bot["timestamp"] = self.timestamp()

        data = {
            "user": user,
            "bot": bot
        }

        if self.log:
            self.update_log(data)

        return data

    def get_response(self, input_text, user_name="user"):
        """
        Return only the response text from the input
        """
        return self.get_response_data(user_name, input_text)["bot"]["text"]


class Terminal(ChatBot):

    def __init__(self):
        super(Terminal, self).__init__()

    def begin(self, user_input="Type something to begin..."):
        import sys

        print(user_input)

        while "exit()" not in user_input:

            # 'raw_input' is just 'input' in python3
            if sys.version_info[0] < 3:
                user_input = str(raw_input())
            else:
                user_input = input()

            bot_input = self.get_response(user_input)
            for line in bot_input:
                print(line.text)


class TalkWithCleverbot(object):

    def __init__(self, log_directory="GitHub/salvius/conversation_engrams/"):
        super(TalkWithCleverbot, self).__init__()
        #from cleverbot.cleverbot import Cleverbot
        from chatterbot.cleverbot.cleverbot import Cleverbot

        self.running = True

        self.cleverbot = Cleverbot()
        self.chatbot = ChatBot()
        self.chatbot.log_directory = log_directory

    def begin(self, bot_input="Hi. How are you?"):
        import time
        from chatterbot.api import clean

        print(self.chatbot.name, bot_input)

        while self.running:
            cb_input = self.cleverbot.ask(bot_input)
            print("cleverbot:", cb_input)
            cb_input = clean(cb_input)

            bot_input = self.chatbot.get_response(cb_input, "cleverbot")
            print(self.chatbot.name, bot_input)
            bot_input = clean(bot_input)

            time.sleep(1.05)
