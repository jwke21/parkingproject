from typing import List
import pandas as pd
import numpy as np

DEFAULT_PATH = 'https://data.seattle.gov/api/views/7jzm-ucez/rows.csv'


class Study:
    def __init__(self, csv_path: str) -> None:
        self._path = csv_path
        self._df = pd.read_csv(csv_path)

    def possible_regions(self) -> List[str]:
        COL = "Study_Area"
        regions = self._df[COL].unique()
        # regions.sort()
        regions = regions.tolist()
        return regions

    def select_region(self, trgt_region: str) -> pd.DataFrame:
        COL = "Study_Area"
        # locate columns whose 'Study_Area' matches the given target region
        region = self._df.loc[(self._df[COL] != np.nan) & \
                             (self._df[COL].str.contains(trgt_region))]

        return region

    def select_street(self):
        pass


if __name__ == "__main__":
    handler = Study(DEFAULT_PATH)

    # print(handler.df)
    # print(handler.df.describe())
    print(handler.select_region("dfsdf"))

