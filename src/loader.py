from data import NetlistProject
from report import Error, ReportEntry


def parse(path):
    return [None, None, None, {Error.DUPLICATE_NAME: ReportEntry(error=Error.DUPLICATE_NAME)}]
    

class Data:
    def __init__(self):
        self._ast_tree = None
        self._parse_tree = None
        self._netlist: NetlistProject = None
        self._errors: dict[Error, ReportEntry] = {}

    @property
    def netlist(self):
        return self._netlist

    @property
    def errors(self):
        return self._errors


class FileData(Data):
    def __init__(self, data_path: str):
        super().__init__()
        self.__load_from_file(data_path)
    
    def __load_from_file(self, data_path: str):
        self._ast_tree, self._parse_tree, self._netlist, self._errors = parse(data_path)


class NetlistData(Data):
    def __init__(self, netlist: NetlistProject):
        super().__init__()
        self._netlist = netlist
