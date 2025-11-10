from loader import Data
from report import Reporter, Error

def check_syntax(data: Data, reporter: Reporter) -> bool:
    if Error.SYNTAX_ERROR in data.errors_after_parse:
        reporter.add_error(data.errors_after_parse[Error.SYNTAX_ERROR])
        return False
    return True
