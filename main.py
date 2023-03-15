from scraper import Scraper
from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pprint import pprint
from consts import API_KEY

YT = build("youtube", "v3", developerKey=API_KEY)

class Main:
    def __init__(self, YT) -> None:
        self.youtube = YT
        self.scraper = Scraper(self.youtube)



main = Main(YT)
pprint(main.scraper.get_regions_categories("US"))










