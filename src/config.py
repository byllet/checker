from loader import Data
from report import Reporter, ReportEntry, Error

def test_check(data: Data, reporter: Reporter) -> bool:
    reporter.add_error(ReportEntry(Error.SYNTAX_ERROR, "something_bad", "main", 100))
    return False

STRATEGIES = [test_check]
