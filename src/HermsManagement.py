from discord.ext import commands
import logging
import discord
  
class HermsManagement(commands.Cog):
  def __init__(self,bot):
    self.bot = bot
    
  
  @commands.command(name='a',brief='adds a user to the hermables list',aliases=['add'])
  async def _command_add_hermable(self, ctx, *args):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.bot.NON_COMMANDER_ERROR)
        return

      new_hermable = ' '.join(args)
      if not self.bot._is_member(new_hermable, ctx):
        await ctx.send(f'"{new_hermable}" does not exist.')
      elif self.bot._is_hermable(new_hermable):
        await ctx.send(f'"{new_hermable}" is already my friend.')
      else:
        self.bot.hermables.add(new_hermable)
        logging.info(f'added new hermable "{new_hermable}"')
        await ctx.send(f'Added new friend "{new_hermable}".')
    except Exception as e:
      logging.error(e, exc_info=True)
      
  
  @commands.command(name='r',brief='removes a user from hermable list',aliases=['remove'])
  async def _command_remove_hermable(self, ctx, *args):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.bot.NON_COMMANDER_ERROR)
        return

      hermable = ' '.join(args)
      if not self.bot._is_hermable(hermable):
        await ctx.send(f'"{hermable}" is not my friend.')
      else:
        self.bot.hermables.remove(hermable)
        logging.info(f'removed hermable "{hermable}"')
        await ctx.send(f'Removed friend "{hermable}".')
    except Exception as e:
      logging.error(e, exc_info=True)
      
  
  @commands.command(name='clear',brief='clears the hermables list')
  async def _command_clear_hermables(self, ctx):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.bot.NON_COMMANDER_ERROR)
      elif len(self.bot.hermables) == 0:
        await ctx.send("I don't have any friends right now.")
      else:
        self.bot.hermables.clear()
        logging.info('cleared hermables')
        await ctx.send("Friends cleared.")
    except Exception as e:
      logging.error(e, exc_info=True)
      
  
  @commands.command(name='list',brief='lists hermables')
  async def _command_list_hermables(self, ctx):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.bot.NON_COMMANDER_ERROR)
      elif len(self.bot.hermables) < 1:
        await ctx.send("I don't have any friends right now.")
      else:
        friends_list = '• ' + '\n• '.join(sorted(self.bot.hermables))
        await ctx.send(f'My friends:\n{friends_list}')
    except Exception as e:
      logging.error(e, exc_info=True)
      
      