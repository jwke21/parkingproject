from csv_handler import Study
from os import path
import pickle

DEFAULT_DF_PATH = './resources/study.df'
CSV_URL = 'https://data.seattle.gov/api/views/7jzm-ucez/rows.csv'


class Program:
    def __init__(self):
        self.study = self._load_df()
        self._program_loop()

    def _load_df(self) -> Study:
        if path.exists(DEFAULT_DF_PATH):
            study = pickle.load(DEFAULT_DF_PATH)
        else:
            study = Study(CSV_URL)
        return study

    def _program_loop(self):
        finished = False
        while not finished:
            region = self._get_usr_trgt_region()

    def _get_primary_street(self):
        pass            

    def _get_usr_trgt_region(self):
        regions = []
        while True:
            trgt_region = input("Please enter the region you are trying to find parking in: ")
            region = self.study.select_region(trgt_region)
            if region.empty:
                print("Could not find that region")
                print("Possible regions include: ")
                if not regions:
                    regions = self.study.possible_regions()
                for i, r in enumerate(regions):
                    print(f"{i}: {r}")
            else:
                return region

if __name__ == "__main__":
    Program()
