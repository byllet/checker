from data import NetlistProject
from report import Error, ReportEntry
from parser import parse


class Data:
    def __init__(self):
        self._ast_tree = None
        self._parse_tree = None
        self._netlist: NetlistProject = None
        self._errors_after_parse: dict[Error, ReportEntry] = {}

    @property
    def netlist(self):
        return self._netlist

    @property
    def errors_after_parse(self):
        return self._errors_after_parse


class FileData(Data):
    def __init__(self, data_path: str):
        super().__init__()
        self.__load_from_file(data_path)
    
    def __load_from_file(self, data_path: str):
        self._ast_tree, self._parse_tree, self._netlist, self._errors_after_parse = parse(data_path)


class NetlistData(Data):
    def __init__(self, netlist: NetlistProject):
        super().__init__()
        self._netlist = netlist
