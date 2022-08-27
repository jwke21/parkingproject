from time import sleep
from typing import List
from datetime import datetime
import pandas as pd
import numpy as np

USED_COLS = [
    0,  # "Elmntkey"
    1,  # "Study_Area"
    3,  # "Date Time"
    5,  # "Unitdesc"
    7,  # "Parking_Spaces"
    8,  # "Total_Vehicle_Count"
]

COL_DTYPES = {
    # "Elmntkey": np.uint32,            # There are 167,799 total rows requiring a uint32
    "Study_Area": str,
    "Date Time": str,                 # Will be converted to date time during cleaning
    "Unitdesc": str,                  # The streets
    "Parking_Spaces": np.float16,     # Available spaces
    "Total_Vehicle_Count": np.float16 # Spaces occupied
}

# COL_NA_VALS = {
#     "Elmntkey": np.nan,
#     "Study_Area": "N/A",
#     "Date Time": "N/A",
#     "Unitdesc": "N/A",
#     "Parking_Spaces": np.nan,
#     "Total_Vehicle_Count": np.nan
# }

DEFAULT_PATH = 'https://data.seattle.gov/api/views/7jzm-ucez/rows.csv'


class Study(object):
    SA = "Study_Area"
    DT = "Date Time"
    DA = "Date"
    TI = "Time"
    ST = "Unitdesc"
    ELK = "Elmntkey"
    PS = "Parking_Spaces"
    VC = "Total_Vehicle_Count"

    def __init__(self, csv_path: str) -> None:
        self._path = csv_path
        self._df = self._load_df(csv_path)
        self._regions = self._possible_regions(self._df)

    def _load_df(self, path: str) -> pd.DataFrame:
        print("reading csv...")
        df = pd.read_csv(path,
                         usecols=USED_COLS,
                         dtype=COL_DTYPES,
                         )
        #TODO: provide some means of cleaning the data
        print("cleaning data...")
        sleep(0.1)
        df = self._clean_df(df)
        return df

    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        INVALID_DT_VALS = [
            "1-00-00 00:00:00",
            ""
        ]

        # remove invalid rows
        df = df.loc[~(df[Study.DT].isin(INVALID_DT_VALS))]
        # convert 'Date Time' from str to DateTime
        self._convert_to_datetime(df, Study.DT)
        return df

    def _convert_to_datetime(self, df: pd.DataFrame, col_name: str) -> None:
        df[col_name] = pd.to_datetime(df[col_name], unit='ns')
        df[col_name] = np.datetime_as_string(df[col_name])

    def _possible_regions(self, df: pd.DataFrame) -> np.ndarray:
        return df[Study.SA].unique()

    def get_regions(self) -> List[str]:
        out = self._regions.tolist()

        for i, r in enumerate(out):
            out[i] = str(r).lower()

        return out

    def select_region(self, trgt_region: str) -> pd.DataFrame:
        # locate columns whose 'Study_Area' matches the given target region
        region = self._df.loc[(self._df[Study.SA] != np.nan) & \
                              (self._df[Study.SA].str.contains(trgt_region))]

        return region

    def is_valid_street(self, street: str) -> bool:
        # determine whether any row's 'Unitdesc' column contains the given street
        return self._df[Study.ST].str.contains(street).any()

    def is_valid_intersection(self, street1: str, street2: str) -> bool:
        # return whether there are any rows whose 'Unitdesc' contain both streets
        return self._get_intersection(street1, street2) is not None
    
    def get_total_spaces(self, street1: str, street2: str) -> float:
        intersection = self._get_intersection(street1, street2)

        # get the total number of parking spaces available around the intersection
        keys = intersection[Study.ELK].unique()
        total = 0
        for key in keys:
            rows = intersection.loc[intersection[Study.ELK] == key]
            total += rows[Study.PS].iloc[0]

        return total

    def get_average_occupancy(self, street1: str, street2: str) -> float:
        intersection = self._get_intersection(street1, street2)
        return intersection[Study.VC].mean()

    def _get_intersection(self, street1: str, street2: str) -> pd.DataFrame:
        # get rows whose 'Unitdesc' contains both streets
        return self._df.loc[(self._df[Study.ST].str.contains(street1)) & \
                            (self._df[Study.ST].str.contains(street2))]

    def _get_spots_at_time(self, df: pd.DataFrame, hour: str) -> pd.DataFrame:
        # get the spots that are within 45 minutes of the given time
        return df.loc[df[Study.DT].str.contains(hour)]

    def _available_spots(self, df: pd.DataFrame) -> pd.DataFrame:
        THRESHOLD = 1
        return df.loc[df[Study.PS] - df[Study.VC] >= THRESHOLD]
        
    def _get_confidence(self, avail_recordings: int, total_recordings: int) -> str:
        VERY_HIGH = 90
        HIGH = 75
        MEDIUM = 50
        LOW = 25

        # edge case where there is no recorded data
        # reasoning: if there was no one surveying the time is likely to be too early or too
        #            late for anyone to be occupying the space (e.g. 01:00)
        if not total_recordings:
            return HIGH

        percentage_open = (avail_recordings / total_recordings) * 100

        # conversion of percentage into confidence level 
        if percentage_open >= VERY_HIGH:
            return "VERY HIGH"
        elif percentage_open >= HIGH:
            return "HIGH"
        elif percentage_open >= MEDIUM:
            return "MEDIUM"
        elif percentage_open >= LOW:
            return "LOW"
        elif percentage_open < LOW:
            return "VERY LOW"

    def calc_free_space_probability(self, street1: str, street2: str, time: str) -> str:
        # get rows for intersectionf
        intersection = self._get_intersection(street1, street2)
        dt_time = datetime.strptime(time, "%H:%M")
        time = dt_time.strftime("%H:%M")
        # get rows within specified hour
        # datetime.strptime(time, format=)
        # std_time = pd.to_datetime(time)
        # std_time = std_time.to_datetime64()
        # print(std_time)
        # print(type(std_time))
        # print(std_time.hour)
        print(time)
        intersection = self._get_spots_at_time(intersection, time[:3])
        avail_spots = self._available_spots(intersection)
        return self._get_confidence(len(avail_spots), len(intersection))


# if __name__ == "__main__":
    # handler = Study(DEFAULT_PATH)

    # print(handler._df)
    # print(handler._df.dtypes)
    # print(handler.calc_free_space_probability("TERRY AVE", "HARRISON ST", "17:00"))
    # print(handler.get_total_spaces("TERRY AVE", "HARRISON ST"))
    # print(handler.get_average_occupancy("TERRY AVE", "HARRISON ST"))
    # print(handler._df.describe())
    # print(handler.select_region("dfsdf"))

