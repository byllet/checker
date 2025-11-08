import data
from loader import Data
from report import Reporter, Error


def check_incomplete_hierarchy(data: Data, reporter: Reporter):
    if Error.MISSING_BLOCK in data.errors_after_parse:
        reporter.add_error(data.errors_after_parse[Error.MISSING_BLOCK])
        return False
    return True

def check_hierarchy_loop(data: Data, reporter: Reporter):
    pass

if (__name__ == "__main__"):
    PRIMITIVES = {
    "transistor": data.Block("transistor", is_primitive=True, primitive_pins=["a", "b", "c"])
    }
    transistor = PRIMITIVES["transistor"]
    #------------

    nl = data.NetlistProject("netlist", primitive_blocks=PRIMITIVES)
    main = nl.add_block("main")
    # print(main.blocks)

    try:
        nl.add_block("main")
    except Exception as e:
        print(e)

