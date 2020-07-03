from discord.ext import commands
import logging
import discord
  
class TestCog(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
  
  @commands.command(name='f',brief='does a foo',aliases=['foo'])
  async def foo(self, ctx):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
      else:
        await ctx.channel.send(f'Foo')
    except Exception as e:
      logging.error(e, exc_info=True)