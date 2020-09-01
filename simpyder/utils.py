import logging
from os.path import dirname, join
from .__version__ import __VERSION__
DEFAULT_UA = 'Simpyder {}'.format(__VERSION__)
FAKE_UA = 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

# The background is set with 40 plus the number of the color, and the foreground with 30

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message, use_color=True):
  if use_color:
    message = message.replace(
        "$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
  else:
    message = message.replace("$RESET", "").replace("$BOLD", "")
  return message


COLORS = {
    'WARNING': YELLOW,
    'INFO': CYAN,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}


class ColoredFormatter(logging.Formatter):
  def __init__(self, msg, use_color=True):
    logging.Formatter.__init__(self, msg)
    self.use_color = use_color

  def format(self, record):
    levelname = record.levelname
    if self.use_color and levelname in COLORS:
      levelname_color = COLOR_SEQ % (
          30 + COLORS[levelname]) + levelname + RESET_SEQ
      record.levelname = levelname_color
    return logging.Formatter.format(self, record)


# Custom logger class with multiple destinations
class ColoredLogger(logging.Logger):
  FORMAT = "[%(asctime)s][%(levelname)s] @ %(name)s: %(message)s"
  COLOR_FORMAT = formatter_message(FORMAT, True)

  def __init__(self, name):
    logging.Logger.__init__(self, name, logging.INFO)
    color_formatter = ColoredFormatter(self.COLOR_FORMAT)
    console = logging.StreamHandler()
    console.setFormatter(color_formatter)
    self.addHandler(console)
    return


def _get_logger(name, level='INFO'):
  logging.setLoggerClass(ColoredLogger)
  logger = logging.getLogger(name)
  logger.setLevel(level)
  return logger
