from copy import deepcopy
from typing import  List
from report import Reporter, Report
from loader import Data, FileData, NetlistData
from data import NetlistProject
from config import STRATEGIES


def _check(strategies: List[callable], data: Data) -> Report:
    reporter = Reporter()

    for strategy in strategies:
        can_continue = strategy(data, reporter)
        if not can_continue: 
            break

    return reporter.get_report()


class FileChecker:
    def __init__(self, data_path: str):
        self.__data: Data = FileData(data_path=data_path)
        self.__strategies = deepcopy(STRATEGIES)

    def check(self) -> Report:
        return _check(self.__strategies, self.__data)

    def get_object_model(self) -> NetlistProject:
        return self.__data.netlist
    

class NetlistChecker:
    def __init__(self, netlist: NetlistProject):
        self.__data = NetlistData(self.__netlist)
        self.__strategies = [lambda data, reporter: False]
        self.__netlist = netlist

    def check(self) -> Report:
        return _check(self.__strategies, self.__data)
