from loader import Data, NetlistData
from data import NetlistProject, Block, Instance
from report import Reporter, ReportEntry
from typing import List
from parser.resources.report import Error

def check_network_correctness(data: Data, reporter: Reporter) -> bool:
    """Функция проверки сети на корректность цепей по формату нетлиста,
    является одной из проверок чекера и вызывается в ходе работы чекера"""
    status: bool = True
    
    netlist = data.netlist
    if netlist is None:
        return status
    
    blocks = netlist.blocks

    root_blocks = __find_root_blocks(blocks)
    if len(root_blocks) != 1:
        status = False
        report = ReportEntry(
            error=Error.MISSING_BLOCK,
            message="Root block is not found or too many blocks may be the root block"
        )
        reporter.add_error(report)
        return False
    
    if not __check_multiple_nets_per_pin(blocks, reporter):
        status = False
    
    return status


def check_network_connection(data: Data, reporter: Reporter) -> bool:
    """Функция проверки сети на подключение всех цепей
    является одной из проверок чекера и вызывается в ходе работы чекера"""
    status: bool = True

    netlist = data.netlist
    if netlist is None:
        return status
    blocks = netlist.blocks

    root_blocks = __find_root_blocks(blocks)

    if len(root_blocks) != 1:
        status = False
        report = ReportEntry(
            error=Error.MISSING_BLOCK,
            message="Root block is not found or too many blocks may be the root block"
        )
        reporter.add_error(report)
        return False

    if not __check_orphaned_nets(netlist, reporter, root_blocks[0]):
        status = False
    
    return status


def __find_root_blocks(blocks : List[Block]) -> List[str]:
    """
    Находит все "корневые" блоки нетлиста.
    Корневой блок - это блок, который не используется как тип инстанса
    ни в одном другом блоке
    Приватная функция
    """

    blocks_used_as_types = set()
    for block_name in blocks.keys():
        block = blocks[block_name]

        if block.is_primitive:
            continue
            
        for instance in block.instances.values():
            blocks_used_as_types.add(instance.type.name)
    
    root_blocks = [block for block in blocks.keys()
        if block not in blocks_used_as_types]
    
    return root_blocks


def __check_orphaned_nets(netlist : NetlistProject, reporter : Reporter, root_block : str) -> bool:
    """
    Рекурсивная проверка корректности цепей.
    Цепь считается корректной, если она соединяет минимум 2 пина в начальном блоке
    Ловит 'крюки'
    Приватная функция
    """
    status = True
    blocks = netlist.blocks
    
        
    main_block = blocks[root_block]
    
    def count_real_terminals(current_block, net_name, visited_nets):
        if (current_block.name, net_name) in visited_nets:
            return 0
        
        visited_nets.add((current_block.name, net_name))
        
        if net_name not in current_block.nets:
            return 0
            
        net = current_block.nets[net_name]
        terminals_count = 0
        
        for pin_ref in net.pins.values():
            if pin_ref.ref_parent is None:
                if current_block.name == root_block:
                    terminals_count += 1
                pass
                
            else:
                instance = pin_ref.ref_parent
                
                if instance.type.is_primitive:
                    continue
                
                child_block = instance.type
                child_pin_name = pin_ref.name
                    
                child_net_name = None
                if child_pin_name in child_block.interface_pins:
                    child_pin_ref = child_block.interface_pins[child_pin_name]
                    if child_pin_ref.net:
                        child_net_name = child_pin_ref.net.name
                    
                if child_net_name:
                    terminals_count += count_real_terminals(child_block, child_net_name, visited_nets)
                else:
                    pass
                        
        return terminals_count

    for net_name in main_block.nets:
        visited = set()
        total_terminals = count_real_terminals(main_block, net_name, visited)
        
        if total_terminals == 0:
            report = ReportEntry(
                error=Error.ORPHANED_NET,
                message=f"Incorrect net '{net_name}' in {root_block}: connects {total_terminals} end points",
                location=f"{root_block}.{net_name}"
            )
            reporter.add_error(report)
            status = False
            
    return status



def __check_multiple_nets_per_pin(blocks: List[Block], reporter: Reporter) -> bool:
    """Функция проверки подключения пина к нескольким цепям.
    
    Проверяет, что каждый пин подключен максимум к одной цепи.
    """
    status = True

    for block_name, block in blocks.items():
        if block.is_primitive:
            continue

        if not __check_pin_multiple_nets_in_block(block, reporter):
            status = False

    return status


def __check_pin_multiple_nets_in_block(block: Block, reporter: Reporter) -> bool:
    """Проверка подключения пинов к нескольким цепям в блоке"""
    status = True
    pin_to_nets = {}
    
    for net_name, net in block.nets.items():
        for pin_ref in net._Net__pins:
            if pin_ref.ref_parent is None:
                pin_id = f"interface.{pin_ref.name}"
            elif isinstance(pin_ref.ref_parent, Instance):
                pin_id = f"{pin_ref.ref_parent.name}.{pin_ref.name}"
            else:
                pin_id = f"interface.{pin_ref.name}"
            
            if pin_id not in pin_to_nets:
                pin_to_nets[pin_id] = []
            pin_to_nets[pin_id].append(net_name)
    
    for pin_id, net_names in pin_to_nets.items():
        if len(set(net_names)) > 1:
            unique_nets = sorted(set(net_names))
            report = ReportEntry(
                error=Error.PIN_MISMATCH,
                message=f"Pin '{pin_id}' is connected to multiple nets: {', '.join(unique_nets)}",
                location=f"{block.name}.{pin_id}"
            )
            reporter.add_error(report)
            status = False

    return status