from discord.ext import commands
import logging
import discord
  
class ServerCommands(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    
  
  @commands.command(name='j',brief='joins herm_bot',aliases=['join'])
  async def _command_join(self, ctx):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.bot.NON_COMMANDER_ERROR)
      elif ctx.author.voice is None: ###
        await ctx.send("You are not in a voice channel.") ###
      elif self.bot.voice_client is not None and self.bot.voice_client.channel.name == ctx.author.voice.channel.name:
        await ctx.send("I'm already in your voice channel.")
      else:
        if self.bot.voice_client is not None:
          await self.bot._leave_voice_channel()

        await self.bot._join_voice_channel(ctx.author.voice.channel)
        self.bot.voice_client.listen(discord.reader.ConditionalFilter(self.bot.vad_sink, self.bot._should_herm_user))
    except Exception as e:
      logging.error(e, exc_info=True)
      
      
  @commands.command(name='l',brief='leaves herm_bot',aliases=['leave'])
  async def _command_leave(self, ctx):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.bot.NON_COMMANDER_ERROR)
      elif self.bot.voice_client is None:
        await ctx.send("I'm not currently in a voice channel.")
      else:
        await self.bot._leave_voice_channel()
    except Exception as e:
      logging.error(e, exc_info=True)