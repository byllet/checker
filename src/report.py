from dataclasses import dataclass
from enum import Enum
from data import Block
from typing import  Optional, List


class Status(Enum):
    OK = "OK"
    ERROR = "ERROR"


class Error(Enum):
    SYNTAX_ERROR = "SYNTAX_ERROR"
    HIERARCHY_CYCLE = "HIERARCHY_CYCLE"
    MISSING_BLOCK = "MISSING_BLOCK"
    PIN_MISMATCH = "PIN_MISMATCH"
    DISCONNECTED_PIN = "DISCONNECTED_PIN"
    ORPHANED_NET = "ORPHANED_NET"
    DUPLICATE_NAME = "DUPLICATE_NAME"


class Report:
    def __init__(self, report_entries : List["ReportEntry"]):
        self.report_entries = report_entries
        self.__get_state()


    def __get_state(self):
        if len(self.report_entries) > 0:
            self.status = Status.ERROR
        
    def to_dict(self):
        res = {}
        res["status"] = self.status
        res["errors"] = []

        for report in self.report_entries:
            entry = f"error: {report.error} \n" \
                    f"line: {report.line} \n" \
                    f"location: {report.location} \n" \
                    f"message: {report.message}"
            res["errors"].append(entry)
        
        return res

    
    def __str__(self):
        d = self.to_dict()
        str = f"status: {d["status"]}\n"
        for entry in d["errors"]:
            str += entry
        
        return str


@dataclass
class ReportEntry:
    error : Error = None
    message : Optional[str] = None
    location: Optional[str] = None
    line : Optional[int] = None



class Reporter:
    def __init__(self):
        self.__reports = []

    def add_error(self, report_entry : ReportEntry):
        self.__reports.append(report_entry)

    def get_report(self) -> Report:
        return Report(self.__reports)
