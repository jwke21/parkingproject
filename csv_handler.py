from typing import List
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
#     "Elmntkey": np.uint32,            # There are 167,799 total rows requiring a uint32
    "Study_Area": str,
    # "Date Time": np.datetime64,                 # Will be converted to date time during cleaning
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
        return df

    def _possible_regions(self, df: pd.DataFrame) -> np.ndarray:
        COL = "Study_Area"
        return df[COL].unique()

    def get_regions(self) -> List[str]:
        out = self._regions.tolist()

        for i, r in enumerate(out):
            out[i] = str(r).lower()

        return out

    def select_region(self, trgt_region: str) -> pd.DataFrame:
        COL = "Study_Area"
        # locate columns whose 'Study_Area' matches the given target region
        region = self._df.loc[(self._df[COL] != np.nan) & \
                              (self._df[COL].str.contains(trgt_region))]

        return region

    def is_valid_street(self, street: str) -> bool:
        COL = "Unitdesc"
        # determine whether any row's 'Unitdesc' column contains the given street
        return self._df[COL].str.contains(street).any()

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

    def _get_intersection(self, street1:str, street2: str) -> pd.DataFrame:
        COL = "Unitdesc"
        # get rows whose 'Unitdesc' contains both streets
        return self._df.loc[(self._df[COL].str.contains(street1)) & \
                            (self._df[COL].str.contains(street2))]

if __name__ == "__main__":
    handler = Study(DEFAULT_PATH)

    print(handler._df)
    print(handler.get_total_spaces("TERRY AVE", "HARRISON ST"))
    print(handler.get_average_occupancy("TERRY AVE", "HARRISON ST"))
    # print(handler._df.describe())
    # print(handler.select_region("dfsdf"))

