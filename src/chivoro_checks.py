from data import NetlistProject, Instance, Block
from loader import Data, NetlistData
from report import Reporter, Error


def check_incomplete_hierarchy(data: Data, reporter: Reporter):
    """Проверка на неполноту иерархии"""
    if Error.MISSING_BLOCK in data.errors_after_parse:
        reporter.add_error(data.errors_after_parse[Error.MISSING_BLOCK])
        return True
    return False


def check_cycle_hierarchy(data: Data, reporter: Reporter):
    """Проверка на зацикленность иерархии"""
    all_blocks = data.netlist.blocks
    global_visited = set()
    
    for block in all_blocks.values():
        if block not in global_visited:
            component_visited = set()
            recursion_stack = set()
            if has_cycle_in_component(block, component_visited, recursion_stack):
                reporter.add_error(Error.HIERARCHY_CYCLE)
                return True
                
            global_visited.update(component_visited)
    
    return False

def has_cycle_in_component(block: Block, visited, recursion_stack):
    """Проверка внутри компоненты связности"""
    if block in recursion_stack:
        return True
    if block in visited:
        return False
    
    visited.add(block)
    recursion_stack.add(block)

    for child in block.instances.values():
        if has_cycle_in_component(child.type, visited, recursion_stack):
            return True
    
    recursion_stack.remove(block)
    return False


if (__name__ == "__main__"):
    PRIMITIVES = {
        "transistor": Block("transistor", is_primitive=True, primitive_pins=["a", "b", "c"])
    }
    transistor = PRIMITIVES["transistor"]
    #------------

    nl = NetlistProject("netlist", primitive_blocks=PRIMITIVES)
    block1 = nl.add_block("block1")
    block2 = nl.add_block("block2")
    block3 = nl.add_block("block3")

    b2 = nl.add_instance_to_block("block1", "b2", "block2")
    b3 = nl.add_instance_to_block("block2", "b3", "block3")
    b_test = nl.add_instance_to_block("block1", "b_test", "block3")
    b_error = nl.add_instance_to_block("block3", "b_error", "block1")

    data_example = NetlistData(nl)
    reporter = Reporter()

    print(check_cycle_hierarchy(data_example, reporter))
    # print(reporter.get_report().to_dict())


