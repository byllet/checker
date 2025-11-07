from loader import Data
from report import Reporter, ReportEntry, Error

def check_any(data: Data, reporter: Reporter) -> bool:
    reporter.add_error(ReportEntry(Error.SYNTAX_ERROR, "something_bad", "main", 100))
    reporter.add_error(ReportEntry(Error.DUPLICATE_NAME, "something_bad", "block3"))
    reporter.add_error(ReportEntry(error=Error.MISSING_BLOCK, message=None, location="block2", line=-13))
    reporter.add_error(ReportEntry(error=Error.MISSING_BLOCK))
    return False

def check_with_errors(data: Data, reporter: Reporter):
    if Error.DUPLICATE_NAME in data.errors:
        reporter.add_error(ReportEntry(Error.DUPLICATE_NAME, message="bla bla"))
        return True
    return False
    

STRATEGIES = [check_with_errors, check_any]
