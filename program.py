from time import sleep
from typing import List
from csv_handler import Study
from os import path
import pickle
import re

DEFAULT_DF_PATH = './resources/study.df'
CSV_URL = 'https://data.seattle.gov/api/views/7jzm-ucez/rows.csv'


class Program(object):
    def __init__(self, data_path: str):
        self._study = self._load_study(data_path)

    @property
    def study(self) -> Study:
        return self._study

    def _load_study(self, data_path: str) -> Study:
        print("loading study data...")
        sleep(0.1)
        if path.exists(data_path):
            print("loading previously saved study...")
            sleep(0.1)
            with open(data_path, 'rb') as src:
                study = pickle.load(src)
        else:
            print("pulling data from internet...")
            sleep(0.1)
            study = Study(CSV_URL)
        return study

    def program_loop(self):
        print("launching program...")
        sleep(0.1)
        while True:
            print("\nType Ctrl^c to close program at any time.\n")
            # region = self._get_usr_trgt_region()
            street1, street2 = self._get_usr_trgt_streets()
            # get basic parking stats about the area around the area around the intersection
            self._show_basic_stats(street1, street2)
            # access data about that zone at a user-specified time
            self._get_time_data(street1, street2)
            if self._close_program_check():
                break

    def _close_program_check(self):
        YES = ("yes", "y")
        NO = ("no", "n")

        usr = input("Would you like to close the program? [y/N] ")
        if usr in YES:
            return True
        elif usr in NO:
            return False
        else:
            print("Invalid input.")

    def _get_time_data(self, street1: str, street2: str) -> None:
        print("Please enter an estimated time using 24-hour (i.e. HH:MM)"
              " format or type 'back' to check a different area:")
        while True:
            usr_time = input("> ").lower()
            if usr_time == "back" or usr_time == "b":
                print("returning to street selection...")
                sleep(0.1)
                break
            if not self._validate_time_input(usr_time):
                print("Invalid input... Correct format: HH:MM")
                sleep(0.5)
            else:
                confidence = self._study.calc_free_space_probability(street1, street2, usr_time)
                print(f"Your likelihood of finding parking at {usr_time} is: {confidence}")
                break

    def _validate_time_input(self, input: str) -> bool:
        # regex for valid 24-hour time input as HH:MM
        VALID_INPUT = r"^(([2]{1}[0-3]{1})|([0-1]{1}[0-9]{1})|([0-9]{1})):([0-5]{1}[0-9]{1}|[0-9]{1})$"

        match = re.search(VALID_INPUT, input)

        return match is not None

    def _show_basic_stats(self, street1: str, street2: str) -> None:
        # get total spaces available around given intersection
        avail_spaces = self._study.get_total_spaces(street1, street2)
        # average number of spots occupied for all times at specified zone
        avg_occupancy = self._study.get_average_occupancy(street1, street2)
        # inform the user of some basic stats about that zone
        print(f"Estimated total possible parking spaces: {avail_spaces}")
        print(f"Average number of spots taken for all recorded times: {avg_occupancy}")

    def _get_usr_trgt_streets(self) -> List[str]:
        print("Searching by intersection.")
        sleep(0.1)
        while True:
            print("Please enter the name of the first street:")
            p_street = self._get_street()
            print("Please enter the name of the second street:")
            s_street = self._get_street()
            if not self._study.is_valid_intersection(p_street, s_street):
                print("Could not find that intersection!")
            else:
                break
        return [p_street, s_street]

    def _get_street(self):
        while True:
            street = input("> ").upper()
            if not self._study.is_valid_street(street):
                print("Could not find that street!")
            else:
                break
        return street

    def _get_usr_trgt_region(self):
        regions = self._study.get_regions()
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



class Loader(object):
    @staticmethod
    def launch_program(df_path=DEFAULT_DF_PATH) -> Program:
        return Program(df_path)

    @staticmethod
    def save_program(program: Program):
        print(f"saving study data to: {DEFAULT_DF_PATH}")
        with open(DEFAULT_DF_PATH, 'wb') as dest:
            pickle.dump(program.study, dest)


if __name__ == "__main__":
    try:
        program = Loader.launch_program()
        program.program_loop()
        Loader.save_program(program)
    except KeyboardInterrupt:
        Loader.save_program(program)
