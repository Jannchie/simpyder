from .config import SimpyderConfig


class Scheduler():
  def __init__(self, spiders=[]):
    super().__init__()
    self.spiders = spiders

  def run_spiders(self):
    for each_spider in self.spiders:
      each_spider.run()
