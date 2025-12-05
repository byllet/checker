from loader import Data, NetlistData
from data import NetlistProject, Block
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
    
    if not __check_incorrect_nets(netlist, reporter, root_blocks[0]):
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

    if not __check_orphaned_nets_recursive(netlist, reporter, root_blocks[0]):
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


def __check_incorrect_nets(netlist : NetlistProject, reporter : Reporter, root_block : str) -> bool:
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
        
        if total_terminals < 2:
            report = ReportEntry(
                error=Error.ORPHANED_NET,
                message=f"Incorrect net '{net_name}' in {root_block}: connects {total_terminals} end points, but should connect at least two",
                location=f"{root_block}.{net_name}"
            )
            reporter.add_error(report)
            status = False
            
    return status


def __check_orphaned_nets_recursive(netlist : NetlistProject, reporter : ReportEntry, root_block : str) -> bool:
    status = True
    blocks = netlist.blocks


    active_nets_global = set()
    
    visited_instances = set()

    queue = [(root_block, root_block, set())]

    while queue:
        block_name, instance_path, active_interface_pins = queue.pop(0)
        
        if block_name not in blocks:
            continue
            
        block = blocks[block_name]
        visited_instances.add(instance_path)
        
        current_block_active_nets = set()
        
        if block_name == root_block:
            for net_name in block.nets:
                current_block_active_nets.add(net_name)
                active_nets_global.add(f"{instance_path}.{net_name}")
        else:
            for net_name, net in block.nets.items():
                for pin_ref in net.pins.values():
                    if pin_ref.ref_parent is None and pin_ref.name in active_interface_pins:
                        current_block_active_nets.add(net_name)
                        active_nets_global.add(f"{instance_path}.{net_name}")
                        break
        
        for inst_name, instance in block.instances.items():
            child_block_name = instance.type.name
            child_path = f"{instance_path}.{inst_name}"
            
            child_active_pins = set()
            
            for pin_name, pin_ref in instance.interface_pins.items():
                if pin_ref.net and pin_ref.net.name in current_block_active_nets:
                    child_active_pins.add(pin_name)
            
            queue.append((child_block_name, child_path, child_active_pins))
    
    check_queue = [(root_block, root_block)]
    
    while check_queue:
        block_name, instance_path = check_queue.pop(0)
        if block_name not in blocks: continue
        block = blocks[block_name]
        
        for net_name, net in block.nets.items():
            if len(net.pins) == 0:
                report = ReportEntry(
                    error=Error.ORPHANED_NET,
                    message=f"Net '{net_name}' in '{instance_path}' is empty",
                    location=f"{instance_path}.{net_name}"
                )
                reporter.add_error(report)
                status = False
                continue

            global_net_id = f"{instance_path}.{net_name}"
            
            if global_net_id not in active_nets_global:
                report = ReportEntry(
                    error=Error.ORPHANED_NET,
                    message=f"Net '{net_name}' in instance '{instance_path}' is not connected to the {root_block} block hierarchy",
                    location=f"{instance_path}.{net_name}"
                )
                reporter.add_error(report)
                status = False
        
        for inst_name, instance in block.instances.items():
            check_queue.append((instance.type.name, f"{instance_path}.{inst_name}"))

    return status
