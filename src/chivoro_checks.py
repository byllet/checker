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

    # несвязный граф 
    nl1 = NetlistProject("netlist_without_connections", primitive_blocks=PRIMITIVES)
    block1 = nl1.add_block("block1")
    block2 = nl1.add_block("block2")
    block3 = nl1.add_block("block3")

    data1 = NetlistData(nl1)
    reporter = Reporter()
    print(check_cycle_hierarchy(data1, reporter))

    # связный граф без цикл.зависимостей 
    nl2 = NetlistProject("netlist_without_cycles", primitive_blocks=PRIMITIVES)
    block1 = nl2.add_block("block1")
    block2 = nl2.add_block("block2")
    block3 = nl2.add_block("block3")
    
    b2 = nl2.add_instance_to_block("block1", "b2", "block2")
    b3 = nl2.add_instance_to_block("block2", "b3", "block3")
    b3_test = nl2.add_instance_to_block("block1", "b3_test", "block3")
    data2 = NetlistData(nl2)
    reporter = Reporter()
    print(check_cycle_hierarchy(data2, reporter))
   
    #связный граф с циклической зависимостью
    nl3 = NetlistProject("netlist_with_cycles", primitive_blocks=PRIMITIVES)
    block1 = nl3.add_block("block1")
    block2 = nl3.add_block("block2")
    block3 = nl3.add_block("block3")
    
    b2 = nl3.add_instance_to_block("block1", "b2", "block2")
    b3 = nl3.add_instance_to_block("block2", "b3", "block3")
    b3_error = nl3.add_instance_to_block("block3", "b3_error", "block1")
    data3 = NetlistData(nl3)
    reporter = Reporter()
    print(check_cycle_hierarchy(data3, reporter))
    
    #граф с несколькими компонентами связности
    nl4 = NetlistProject("test_netlist", primitive_blocks=PRIMITIVES)
    block1 = nl4.add_block("block1")
    block2 = nl4.add_block("block2")
    block3 = nl4.add_block("block3")
    block4 = nl4.add_block("block4")
    block5 = nl4.add_block("block5")
    block6 = nl4.add_block("block6")

    b2 = nl4.add_instance_to_block("block1", "b2", "block2")
    b3 = nl4.add_instance_to_block("block2", "b3", "block3")
    b5 = nl4.add_instance_to_block("block4", "b5", "block5")
    b6 = nl4.add_instance_to_block("block5", "b5", "block6")

    data4 = NetlistData(nl4)
    reporter = Reporter()
    print(check_cycle_hierarchy(data4, reporter))

    # проверка корректности заполнения visited
    nl5 = NetlistProject("simple_netlist", primitive_blocks = PRIMITIVES)
    block1 = nl5.add_block("block1")
    block2 = nl5.add_block("block2")
    
    b2 = nl5.add_instance_to_block("block1", "b2", "block2")
    b1 = nl5.add_instance_to_block("block2", "b1", "block1")
    data5 = NetlistData(nl5)
    reporter = Reporter()
    print(check_cycle_hierarchy(data5, reporter))


