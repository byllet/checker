from copy import deepcopy
from report import Reporter, Report
from loader import Data
from data import NetlistProject
from config import STRATEGIES


class Checker:
    def __init__(self, data_path : str):
        self.__data: Data = Data(data_path)
        self.__reporter: Reporter = Reporter()
        self.__strategies = deepcopy(STRATEGIES)

    def check(self) -> Report:
        self.__reporter = Reporter()
    
        for check in self.__strategies:
            can_continue = check(self.__data, self.__reporter)
            if not can_continue: 
                break

        return self.__reporter.get_report()

    def get_object_model(self) -> NetlistProject:
        return self.__data.net_list
