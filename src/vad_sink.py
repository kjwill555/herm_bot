import discord
import logging

class VadSink(discord.reader.AudioSink):

  callback = None
  latched = False

  def __init__(self, callback):
    self.callback = callback

    super().__init__()


  def write(self, data):
    if type(data.packet) is discord.rtp.RTPPacket:
      if not self.latched:
        logging.debug('latched')
        self.callback()
        self.latched = True
    elif type(data.packet) is discord.rtp.SilencePacket:
      if self.latched:
        self.latched = False
        logging.debug('unlatched')
