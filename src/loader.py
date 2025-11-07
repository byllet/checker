from dataclasses import dataclass
from data import NetlistProject


def parse(path):
    return [None, None, None]


class Data:
    def __init__(self, data_path : str):
        self.ast_tree = None
        self.parse_tree = None
        self.net_list: NetlistProject = None

        [self.ast_tree, self.parse_tree, self.net_list] = parse(data_path)

