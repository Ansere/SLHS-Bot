from discord.colour import Color
from discord import Embed

class ErrorEmbed():
    def __init__ (self, errormsg = "", title = "Something went wrong...", color = Color.red()):
        self.errormsg = errormsg
        self.title = title
        self.color = color

    def getembed(self):
        return Embed(color=self.color, title=self.title, description= self.errormsg)