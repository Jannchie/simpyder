import logging
from os.path import dirname, join
from .__version__ import __VERSION__
DEFAULT_UA = 'Simpyder {}'.format(__VERSION__)
FAKE_UA = 'Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'


def _get_logger(name, level='INFO'):
  logger = logging.getLogger(name)
  ch = logging.StreamHandler()
  ch.setFormatter(logging.Formatter(
      '[%(asctime)s] %(levelname)s @ %(name)s: %(message)s'))
  logger.setLevel(level)
  ch.setLevel(level)
  logger.addHandler(ch)
  if('主线程' not in name):
    logger.critical("线程启动")
  return logger
