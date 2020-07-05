import argparse
import asyncio
import logging
import os
import random
import sys
from vad_sink import VadSink

import discord
from discord.ext import commands
from HermablesManagement import HermablesManagement
from ServerCommands import ServerCommands
from RNG import RNG

class HermBot(commands.Bot):

  CHANNEL_NAME = "the joe biden experience"
  GUILD_NAME = "UCI Triangle"
  HERMABLE_ROLE = "minecraft steve"
  HERMS_DIR = "./herms/"
  NON_COMMANDER_ERROR = "no"

  COMMANDERS = {
    'HoboWithWifi',
    'kjwill555',
    'lightfire456',
    'sandrew',
    'Snail 2',
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

    super().__init__(command_prefix='~')
    
    self.add_cog(HermablesManagement(self))
    self.add_cog(ServerCommands(self))
    self.add_cog(RNG(self))


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


  async def on_voice_state_update(self, member, before, after):
    try:
      if self.voice_client is not None and before.channel is not None and after.channel is None and before.channel.name == self.voice_client.channel.name and len(self.voice_client.channel.members) == 1:
        logging.info(f'no more people in {self.voice_client.channel.name}, leaving')
        await self._leave_voice_channel()
    except Exception as e:
      logging.error(e, exc_info=True)


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
