from typing import List
from csv_handler import Study
from os import path
import pickle

DEFAULT_DF_PATH = './resources/study.df'
CSV_URL = 'https://data.seattle.gov/api/views/7jzm-ucez/rows.csv'


class Program(object):
    def __init__(self, data_path: str):
        self.study = self._load_study(data_path)

    def _load_study(self, data_path: str) -> Study:
        print("loading study data...")
        if path.exists(data_path):
            with open(data_path, 'rb') as src:
                study = pickle.load(src)
        else:
            study = Study(CSV_URL)
        return study

    def program_loop(self):
        print("launching program...")
        finished = False
        while not finished:
            region = self._get_usr_trgt_region()
            street1, street2 = self._get_usr_trgt_streets()
            # get basic parking stats about the area around the area around the intersection
            self._show_basic_stats(street1, street2)
            # access data about that zone at a user-specified time


    def _show_basic_stats(self, street1: str, street2: str) -> None:
        # get total spaces available around given intersection
        avail_spaces = self.study.get_total_spaces(street1, street2)
        # average number of spots occupied for all times at specified zone
        avg_occupancy = self.study.get_average_occupancy(street1, street2)
        # inform the user of some basic stats about that zone
        print(f"Estimated total possible parking spaces: {avail_spaces}")
        print(f"Average number of spots taken for all times: {avg_occupancy}")

    def _get_usr_trgt_streets(self) -> List[str]:
        print("Search by intersection.")
        while True:
            print("Please enter the name of the first street:")
            p_street = self._get_street()
            print("Please enter the name of the second street:")
            s_street = self._get_street()
            if not self.study.is_valid_intersection(p_street, s_street):
                print("Could not find that intersection!")
            else:
                break
        return [p_street, s_street]

    def _get_street(self):
        while True:
            street = input("> ").upper()
            if not self.study.is_valid_street(street):
                print("Could not find that street!")
            else:
                break
        return street

    def _get_usr_trgt_region(self):
        regions = self.study.get_regions()
        while True:
            trgt_region = input("Please enter the region you are trying to find parking in:\n>  ").lower()
            if trgt_region in regions:
                break
            else:
                print("Could not find that region")
                print("Possible regions include: ")
                for i, r in enumerate(regions):
                    print(f"{i}: {r}")
        return trgt_region

    def get_study(self) -> Study:
        return self.study


class Loader(object):
    @staticmethod
    def launch_program(df_path=DEFAULT_DF_PATH) -> Program:
        return Program(df_path)

    @staticmethod
    def save_program(program: Program):
        with open(DEFAULT_DF_PATH, 'wb') as dest:
            pickle.dump(program.get_study(), dest)


if __name__ == "__main__":
    try:
        program = Loader.launch_program()
        program.program_loop()
    except KeyboardInterrupt:
        Loader.save_program(program)
