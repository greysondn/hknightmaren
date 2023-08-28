import maren
import util as hkUtil

import ruamel.yaml.main as yaml

def main():
    confLoader = yaml.YAML()
    conf = confLoader.load(open("conf.yaml"))
    
    # init bot
    bot = maren.Bot(token=conf["token"], initialChannels=[conf["channel"]])

    # now for the "fun" part - build the options out
    for cmd in conf["commands"]:
        swp = hkUtil.HkCommand(cmd["chatString"], cmd["name"], cmd["description"], cmd["delay"])
        bot.hkcommands.addWithCallback(swp)
    
    # and now I believe we just run the bot
    bot.run()
    
if (__name__ == "__main__"):
    main()