from dataclasses import dataclass
from enum import Enum
from typing import  Optional, List
from parser.resources.report import Error


class Status(Enum):
    OK = "OK"
    ERROR = "ERROR"


@dataclass
class ReportEntry:
    error: Error
    message: Optional[str] = None
    location: Optional[str] = None
    line: Optional[int] = None

    def __str__(self) -> str:
        str = f"{self.error}\n"
        if self.line:
            str += f"line: {self.line}\n" 
        if self.location:
            str += f"location: {self.location}\n" 
        if self.message:
            str += f"message: {self.message}\n"
        
        return str[:-1]


class Report:
    def __init__(self, report_entries: List["ReportEntry"]):
        self.__report_entries = report_entries
        self.__status = Status.OK
        self.__change_status()

    def __change_status(self):
        if len(self.__report_entries) > 0:
            self.__status = Status.ERROR
        
    def to_dict(self):
        return {"status": self.__status, "errors": self.__report_entries}

    def __str__(self):
        out = f"status: {self.__status}\n"
        for i, entry in enumerate(self.__report_entries):
            out += f"error_{i}: " + "{\n" + str(entry) + "\n}\n"

        return out[:-1]


class Reporter:
    def __init__(self):
        self.__reports = []

    def add_error(self, report_entry: ReportEntry):
        self.__reports.append(report_entry)

    def get_report(self) -> Report:
        return Report(self.__reports)
