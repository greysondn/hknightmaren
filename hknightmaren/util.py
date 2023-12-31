import random
import asyncio
from typing import Callable

def nop():
    """Simple do nothing command for no reason at all.
    """
    pass

class HkCommand():
    def __init__(self, chatString:str, name:str, description:str, delay:float, onTimer:Callable[[], None] = nop):
        """Constructor.

        Args:
            chatString (str): string used to issue command to Twitch integration over chat
            name (str): name to present to chat as vote option
            description (str): description to present to chat as vote option
            delay (float): time to pass between offering command again, minimum
            onTimer (Callable[[], None]): function to execute when timer runs out. Default: nop
            
        """
        self.chatString:str     = chatString
        """string used to issue command to Twitch integration over chat"""
        
        self.name:str           = name
        """name to present to chat as vote option"""
        
        self.description:str    = description
        """description to present to chat as vote option"""
        
        self.delay:float        = delay
        """time to pass between offering command again, minimum"""
        
        self.onTimer:Callable[[], None]   = onTimer
        """function to execute when timer runs out. Default: nop"""
    
    async def timer(self):
        """Runs an async timer for self.delay seconds and then executes self.onTimer
        """
        await asyncio.sleep(self.delay)
        self.onTimer()

class HkCommandCollection():
    def __init__(self):
        self.commands:list[HkCommand] = []
        
    def add(self, command:HkCommand):
        self.commands.append(command)
    
    def getRandom(self) -> HkCommand:
        """
        pop and return a random HkCommand from self
        
        Returns:
            HkCommand: an HkCommand
        """
        ret:HkCommand = random.choice(self.commands)
        self.commands.remove(ret)
        return ret
    
    def createAddCallback(self, command:HkCommand) -> Callable[[], None]:
        """Generates the necessary callback to add an HkCommand to this list.

        Args:
            command (HkCommand): Command to be added

        Returns:
            Callable[[], None]: Callable for HkCommand
        """
        def ret():
            self.add(command)
        return ret
    
    def addWithCallback(self, command:HkCommand):
        self.add(command)
        command.onTimer = self.createAddCallback(command)
        
class HkVotingBooth():
    def __init__(self):
        self.VALID_OPTIONS = ["0", "1", "2", "3"]
        
        self.pollsOpen:bool  = False
        self.active:bool     = False
        self.votes:list[int] = [0, 0, 0, 0]
        self.voters:list[str] = []
        self.options:list[HkCommand] = []
        
    def stopVoting(self):
        self.pollsOpen = False
        
    def startVoting(self):
        self.pollsOpen = True
        
    def castVote(self, vote:str, voter:str):
        if (self.pollsOpen):
            if (voter not in self.voters):
                self.votes[int(vote)] += 1
                self.voters.append(voter)
    
    def newVote(self):
        self.options = []
        self.voters = []
        self.votes = [0, 0, 0, 0]
    
    def tallyVotes(self) -> HkCommand:
        # this should have been done externally, but just to be extra sure
        self.stopVoting()
        
        # get first entry with max votes
        maxVal = max(self.votes)
        ind    = self.votes.index(maxVal)
        
        # pop out voted for command option
        ret = self.options.pop(ind)
        
        # run the timer end for the other options
        # this should return it to the options list, unexecuted
        # but if you futzed with it, this is a good point to check for breakage
        for option in self.options:
            option.onTimer()
        
        # return
        return ret