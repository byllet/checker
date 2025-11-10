from data import NetlistProject, Instance, Block
from loader import Data, NetlistData
from report import Reporter, Error


def check_incomplete_hierarchy(data: Data, reporter: Reporter):
    """Проверка на неполноту иерархии"""
    if Error.MISSING_BLOCK in data.errors_after_parse:
        reporter.add_error(data.errors_after_parse[Error.MISSING_BLOCK])
        return False
    return True


def check_cycle_hierarchy(data: Data, reporter: Reporter):
    """Проверка на зацикленность иерархии"""
    all_blocks = data.netlist.blocks
    global_visited = set()
    
    for block in all_blocks.values():
        if block not in global_visited:
            component_visited = set()
            recursion_stack = set()
            if __has_cycle_in_component(block, component_visited, recursion_stack):
                reporter.add_error(Error.HIERARCHY_CYCLE)
                return False
                
            global_visited.update(component_visited)
    
    return True

def __has_cycle_in_component(block: Block, visited, recursion_stack):
    """Проверка внутри компоненты связности"""
    if block in recursion_stack:
        return True
    if block in visited:
        return False
    
    visited.add(block)
    recursion_stack.add(block)

    for child in block.instances.values():
        if __has_cycle_in_component(child.type, visited, recursion_stack):
            return True
    
    recursion_stack.remove(block)
    return False

