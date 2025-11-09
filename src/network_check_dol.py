from loader import Data
from report import Reporter, ReportEntry, Error

def check_network_correctness(data: Data, reporter: Reporter) -> bool:
    """Функция проверки сети на корректность цепей по формату нетлиста,
    является одной из проверок чекера и вызывается в ходе работы чекера"""
    status: bool = True
    
    if data.errors_after_parse != {}:
        report = ReportEntry(
            error=Error.SYNTAX_ERROR,
            message="Cannot start checker checking because of syntax error!"
        )
        reporter.add_error(report)
        return False
    
    netlist = data.netlist
    if netlist is None:
        return status

    blocks = netlist.blocks
    
    if not __check_missing_blocks(blocks, reporter):
        status = False
    
    if not __check_pin_mismatch(blocks, reporter):
        status = False
    
    return status


def check_network_connection(data: Data, reporter: Reporter) -> bool:
    """Функция проверки сети на подключение всех цепей
    является одной из проверок чекера и вызывается в ходе работы чекера"""
    status: bool = True
    
    if data.errors_after_parse != {}:
        report = ReportEntry(
            error=Error.SYNTAX_ERROR,
            message="Cannot start checker checking because of syntax error!"
        )
        reporter.add_error(report)
        return False
    
    netlist = data.netlist
    if netlist is None:
        return status

    blocks = netlist.blocks
    
    if not __check_orphaned_nets(blocks, reporter):
        status = False
    
    return status

def __check_missing_blocks(blocks, reporter):
    """Проверка существования всех используемых блоков,
    является приватной"""
    status = True
    
    for block_name, block in blocks.items():

        if block.is_primitive:
            continue

        for instance_name, instance in block.instances.items():
            instance_type_name = instance.type.name

            if instance_type_name in blocks:
                continue

            report = ReportEntry(
                error=Error.MISSING_BLOCK,
                message=f"Block '{instance_type_name}' used in instance '{instance_name}' does not exist",
                    location=f"{block_name}.{instance_name}"
                )
            reporter.add_error(report)
            status = False
    
    return status


def __check_pin_mismatch(blocks, reporter):
    """Проверка соответствия пинов экземпляров их типам,
    является приватной"""
    status = True
    
    for block_name, block in blocks.items():
        
        if block.is_primitive:
            continue

        for instance_name, instance in block.instances.items():
            instance_type = instance.type
            instance_pins = set(instance.interface_pins.keys())
            type_pins = set(instance_type.interface_pins.keys())
            
            missing_pins = type_pins - instance_pins
            if missing_pins:
                report = ReportEntry(
                    error=Error.PIN_MISMATCH,
                    message=f"Instance '{instance_name}' missing pins: {', '.join(missing_pins)}",
                    location=f"{block_name}.{instance_name}"
                )
                reporter.add_error(report)
                status = False
                
            extra_pins = instance_pins - type_pins
            if extra_pins:
                report = ReportEntry(
                    error=Error.PIN_MISMATCH,
                    message=f"Instance '{instance_name}' has extra pins: {', '.join(extra_pins)}",
                    location=f"{block_name}.{instance_name}"
                )
                reporter.add_error(report)
                status = False
    
    return status


def __check_orphaned_nets(blocks, reporter):
    """Проверка неподключенных цепей,
    является приватной"""
    status = True
    
    for block_name, block in blocks.items():
        if block.is_primitive:
            continue
            
        for net_name, net in block.nets.items():
            pin_count = len(net.pins)
            
            if pin_count == 0:
                report = ReportEntry(
                    error=Error.ORPHANED_NET,
                    message=f"Net '{net_name}' has no connections",
                    location=f"{block_name}.{net_name}"
                )
                reporter.add_error(report)
                status = False
    
    return status