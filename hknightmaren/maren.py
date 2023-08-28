import asyncio

from twitchio import Message
from twitchio.ext import commands

import util as hkUtil

class Bot(commands.Bot):

    def __init__(self, token="ACCESS TOKEN", prefix="?", initialChannels=[""]):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=token, prefix=prefix, initial_channels=initialChannels)
        
        self.vote:hkUtil.HkVotingBooth = hkUtil.HkVotingBooth()
        '''voting booth, for voting'''
        
        self.background_tasks = set()
        '''asyncio tasks that this has deferred to background'''
        
        self.hkcommands:hkUtil.HkCommandCollection = hkUtil.HkCommandCollection()
        '''currently possile random commands'''

    async def event_message(self, message: Message) -> None:
        await super().event_message(message)
        
        if (message.content in self.vote.VALID_OPTIONS):
            self.vote.castVote(str(message.content), str(message.author.name))

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Send a hello back!
        await ctx.send(f'Hello {ctx.author.name}!')
        
    @commands.command()
    async def startVote(self, ctx: commands.Context):
        # confirm we received it
        await ctx.send(f"Received command to start voting process!")
        
        # start entire main vote loop
        self.vote.active = True
        
        # main vote loop
        while (self.vote.active):
            
            # init voting process
            self.vote.newVote()
            
            # announce a new vote incoming
            await ctx.send(f"New vote starts soon!")
            
            # we use four options
            # you would have to change the voting booth to change that
            for i in range(4):
                # pull from hkCommands
                option = self.hkcommands.getRandom()
            
                # print option data into chat
                await ctx.send(f"{i} - {option.name} - {option.description}")
                
                # add option to the voting booth
                self.vote.options.append(option)
            
            # open voting then announce it
            self.vote.startVoting()
            await ctx.send(f"Voting now open! You have two minutes to vote.")
            
            # delay two minutes
            await asyncio.sleep(120)
            
            # announce close of voting, then close it
            await ctx.send(f"Voting is now closed!")
            self.vote.stopVoting()
            
            # tally out votes
            winner = self.vote.tallyVotes()
            
            # announce winner
            await ctx.send(f"{winner.name} won!")
            
            # execute winner
            await ctx.send(f"{winner.chatString}")
            
            # schedule winner's delay into the execution queue
            tsk = asyncio.create_task(winner.timer())
            self.background_tasks.add(tsk)
            tsk.add_done_callback(self.background_tasks.discard)
            
            # now declare wait for next vote and start the delay
            await ctx.send(f"Next vote in five minutes!")
            await asyncio.sleep(300)

    @commands.command()
    async def stopVote(self, ctx: commands.Context):
        self.vote.active = False
        await ctx.send(f"Vote stop command received! Voting stops after current vote!")