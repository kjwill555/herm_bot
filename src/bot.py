import argparse
import asyncio
import logging
import os
import random
import sys
from vad_sink import VadSink

import discord
from discord.ext import commands


class HermBot(commands.Bot):

  CHANNEL_NAME = "general"
  GUILD_NAME = "Backyard Philosophers"
  HERMABLE_ROLE = "minecraft steve"
  HERMS_DIR = "./herms/"
  NON_COMMANDER_ERROR = "no"

  COMMANDERS = {
    'mazonly',
  }

  
  guild = None
  hermables = set()
  num_herms = None
  probability = 5
  token = None
  vad_sink = None
  voice_client = None


  def __init__(self, token):
    self.token = token
    self.vad_sink = VadSink(self.on_voice_activity)
    self.num_herms = len([name for name in os.listdir(self.HERMS_DIR) if os.path.isfile(os.path.join(self.HERMS_DIR, name))])

    discord.opus.load_opus('libopus.so.0')

    self.command_prefix='|'
    super().__init__(command_prefix=self.command_prefix)
    
    self.add_commands()
  
  def add_commands(self):
  #should turn this into some sort of class
    command_list = [
      (self._command_add_hermable,'a','add','adds a user to the hermables list'),
      (self._command_change_probability,'c','change_roll','changes probability of a herm'),
      (self._command_clear_hermables,'clear','','clears the hermables list'),
      (self._command_join,'j','join','joins herm_bot'),
      (self._command_leave,'l','leave','leaves herm_bot'),
      (self._command_list_hermables,'list','','lists hermables'),
      (self._command_print_probability,'p','print_roll','prints the current probability'),
      (self._command_remove_hermable,'r','remove','removes a user from hermable list'),
    ]
    for item in command_list:
      alias = [item[2]] if item[2] != '' else []
      self.add_command(commands.Command(item[0], name=item[1], aliases=alias, brief=item[3],
        description=item[3]))
	

  async def _command_add_hermable(self, ctx, *args):
    try:
      if not self._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
        return

      new_hermable = ' '.join(args)
      if not self._is_member(new_hermable, ctx):
        await ctx.send(f'"{new_hermable}" does not exist.')
      elif self._is_hermable(new_hermable):
        await ctx.send(f'"{new_hermable}" is already my friend.')
      else:
        self.hermables.add(new_hermable)
        logging.info(f'added new hermable "{new_hermable}"')
        await ctx.send(f'Added new friend "{new_hermable}".')
    except Exception as e:
      logging.error(e, exc_info=True)


  async def _command_remove_hermable(self, ctx, *args):
    try:
      if not self._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
        return

      hermable = ' '.join(args)
      if not self._is_hermable(hermable):
        await ctx.send(f'"{hermable}" is not my friend.')
      else:
        self.hermables.remove(hermable)
        logging.info(f'removed hermable "{hermable}"')
        await ctx.send(f'Removed friend "{hermable}".')
    except Exception as e:
      logging.error(e, exc_info=True)


  async def _command_change_probability(self, ctx, new_probability):
    try:
      if not self._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
        return

      new_probability = int(new_probability)
      if new_probability <= 0:
        await ctx.send('New roll must be greater than zero.')
      else:
        self.probability = new_probability
        logging.info(f'Updated probability to {new_probability}')
        await ctx.send(f'Updated roll to d{new_probability}.')
    except ValueError:
      await ctx.send(f'{new_probability} is not an integer.')
    except Exception as e:
      logging.error(e, exc_info=True)


  async def _command_clear_hermables(self, ctx):
    try:
      if not self._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
      elif len(self.hermables) == 0:
        await ctx.send("I don't have any friends right now.")
      else:
        self.hermables.clear()
        logging.info('cleared hermables')
        await ctx.send("Friends cleared.")
    except Exception as e:
      logging.error(e, exc_info=True)


  async def _command_join(self, ctx):
    try:
      if not self._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
      elif ctx.author.voice is None: ###
        await ctx.send("You are not in a voice channel.") ###
      elif self.voice_client is not None and self.voice_client.channel.name == ctx.author.voice.channel.name:
        await ctx.send("I'm already in your voice channel.")
      else:
        if self.voice_client is not None:
          await self._leave_voice_channel()

        await self._join_voice_channel(ctx.author.voice.channel)
        self.voice_client.listen(discord.reader.ConditionalFilter(self.vad_sink, self._should_herm_user))
    except Exception as e:
      logging.error(e, exc_info=True)


  async def _command_leave(self, ctx):
    try:
      if not self._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
      elif self.voice_client is None:
        await ctx.send("I'm not currently in a voice channel.")
      else:
        await self._leave_voice_channel()
    except Exception as e:
      logging.error(e, exc_info=True)


  async def _command_list_hermables(self, ctx):
    try:
      if not self._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
      elif len(self.hermables) < 1:
        await ctx.send("I don't have any friends right now.")
      else:
        friends_list = '• ' + '\n• '.join(sorted(self.hermables))
        await ctx.send(f'My friends:\n{friends_list}')
    except Exception as e:
      logging.error(e, exc_info=True)


  async def _command_print_probability(self, ctx):
    try:
      if not self._is_commander(ctx.author.name):
        await ctx.send(self.NON_COMMANDER_ERROR)
      else:
        await ctx.channel.send(f'Roll is currently d{self.probability}')
    except Exception as e:
      logging.error(e, exc_info=True)


  def _is_commander(self, name):
    return name in self.COMMANDERS


  def _is_hermable(self, name):
    return name in self.hermables


  def _is_member(self, name, ctx):
    return name in [member.name for member in ctx.guild.members]


  async def _join_voice_channel(self, channel):
    self.voice_client = await channel.connect()
    logging.info(f'connected to voice channel "{self.voice_client.channel.name}"')


  async def _leave_voice_channel(self):
    await self.voice_client.disconnect()
    logging.info(f'left voice channel "{self.voice_client.channel.name}"')
    self.voice_client = None

  async def on_ready(self):
    try:
      logging.info(f'{self.user} successfully connected to Discord')
      
      self.guild = discord.utils.get(self.guilds, name=self.GUILD_NAME)
      logging.info(f'guild name: {self.guild.name}')
    except Exception as e:
      logging.error(e, exc_info=True)


  def on_voice_activity(self):
    try:
      roll = random.randint(1, self.probability)
      logging.debug(f'rolled a {roll}')
      if roll == 1:
        herm_num = random.randint(1, self.num_herms)
        self.voice_client.play(discord.FFmpegOpusAudio(f'herms/{herm_num}.ogg'))
    except Exception as e:
      logging.error(e, exc_info=True)


  async def on_voice_state_update(self, member, before, after): ###
    try:
      if self.voice_client is not None and before.channel is not None and after.channel is None and before.channel.name == self.voice_client.channel.name and len(self.voice_client.channel.members) == 1:
        logging.info(f'no more people in {self.voice_client.channel.name}, leaving')
        await self._leave_voice_channel()
    except Exception as e:
      logging.error(e, exc_info=True) ###


  def _should_herm_user(self, voice_data):
    user = voice_data.user
    return user.name in self.hermables


  def start_running(self):
    loop = asyncio.get_event_loop()

    try:
      loop.run_until_complete(self.start(self.token))
    except KeyboardInterrupt:
      pass
    except Exception as e:
      logging.error(e, exc_info=True)
    finally:
      loop.run_until_complete(self.stop_running())


  async def stop_running(self):
    logging.info('stopping...')
    if self.voice_client is not None:
      await self._leave_voice_channel()

    if self.guild is not None:
      await self.logout()
      logging.info(f'logged out of {self.guild.name}')
      self.guild = None


def _prepare_logging(verbose, log_to_console):
  log_format = '%(asctime)s %(funcName)s()_%(lineno)s %(levelname)s: %(message)s'
  date_format = '%m/%d/%Y %I:%M:%S %p'

  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter(log_format, datefmt=date_format)
  if log_to_console:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

  file_handler = logging.FileHandler('logs/log.log')
  file_handler.setLevel(logging.INFO)
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
  parser.add_argument("-c", "--console", help="log to console", action="store_true")
  argv = parser.parse_args()

  _prepare_logging(argv.verbose, argv.console)

  bot = HermBot(os.environ.get('HERM_BOT_TOKEN'))
  bot.start_running()
