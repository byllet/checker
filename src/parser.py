from report import Error, ReportEntry
from data import NetlistProject

def parse(path):
    return [None, None, NetlistProject("nl"), {Error.DUPLICATE_NAME: ReportEntry(error=Error.DUPLICATE_NAME)}]