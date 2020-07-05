from discord.ext import commands
import logging
import discord
  
class RNG(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  
  @commands.command(name='c', brief='changes probability of a herm', aliases=['change_roll'])
  async def _command_change_probability(self, ctx, new_probability):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.bot.NON_COMMANDER_ERROR)
        return

      new_probability = int(new_probability)
      if new_probability <= 0:
        await ctx.send('New roll must be greater than zero.')
      else:
        self.bot.probability = new_probability
        logging.info(f'Updated probability to {new_probability}')
        await ctx.send(f'Updated roll to d{new_probability}.')
    except ValueError:
      await ctx.send(f'{new_probability} is not an integer.')
    except Exception as e:
      logging.error(e, exc_info=True)


  @commands.command(name='p', brief='prints the current probability', aliases=['print_roll'])
  async def _command_print_probability(self, ctx):
    try:
      if not self.bot._is_commander(ctx.author.name):
        await ctx.send(self.bot.NON_COMMANDER_ERROR)
      else:
        await ctx.channel.send(f'Roll is currently d{self.bot.probability}')
    except Exception as e:
      logging.error(e, exc_info=True)