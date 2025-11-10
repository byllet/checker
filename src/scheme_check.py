from data import *
from report import *
from loader import *


"""
Некорректная подсхема. Список пинов инстанса подсхемы не соответствует списку пинов блока этой подсхемы.
Неподключённый пин. 1) Неподключённый внешний пин блока. 2) Неподключённый пин инстанса.
"""



def check_subcircuit_correctness(data: Data, reporter: Reporter) -> bool:
    """Функция проверки соответствия списка пинов инстанса подсхемы списку пинов блока этой подсхемы"""
    status = True

    netlist = data.net_list
    if netlist is None:
        return status

    blocks = netlist.blocks

    if not __check_instance_pin_compatibility(blocks, reporter):
        status = False

    return status


def __check_instance_pin_compatibility(blocks, reporter):
    """Проверка соответствия списка пинов инстанса подсхемы списку пинов блока этой подсхемы,
    является приватной"""
    status = True

    for block_name, block in blocks.items():

        #if block.is_primitive:
        #    continue

        for instance_name, instance in block.instances.items():
            instance_type = instance.type
            instance_pins = set(instance.interface_pins.keys())
            type_pins = set(instance_type.interface_pins.keys())

            if instance_pins != type_pins:
                missing_pins = type_pins - instance_pins
                extra_pins = instance_pins - type_pins

                error_messages = []

                if missing_pins:
                    error_messages.append(f"missing pins: {', '.join(sorted(missing_pins))}")

                if extra_pins:
                    error_messages.append(f"extra pins: {', '.join(sorted(extra_pins))}")

                report = ReportEntry(
                    error=Error.PIN_MISMATCH,
                    message=f"Instance '{instance_name}' pin mismatch: {'; '.join(error_messages)}",
                    location=f"{block_name}.{instance_name}"
                )
                reporter.add_error(report)
                status = False

    return status


def check_pin_connection(data: Data, reporter: Reporter) -> bool:
    """Функция проверки неподключенных пинов:
    1) Неподключённый внешний пин блока
    2) Неподключённый пин инстанса"""
    status = True

    netlist = data.net_list
    if netlist is None:
        return status

    blocks = netlist.blocks

    if not __check_unconnected_block_pins(blocks, reporter):
        status = False

    if not __check_unconnected_instance_pins(blocks, reporter):
        status = False

    return status


def __check_unconnected_block_pins(blocks, reporter):
    """Проверка неподключенных внешних пинов блоков,
    является приватной"""
    status = True

    for block_name, block in blocks.items():
        #if block.is_primitive:
        #    continue

        for pin_name, pin_ref in block.interface_pins.items():
            if pin_ref.net is None:
                report = ReportEntry(
                    error=Error.DISCONNECTED_PIN,
                    message=f"Block interface pin '{pin_name}' is not connected to any net",
                    location=f"{block_name}.{pin_name}"
                )
                reporter.add_error(report)
                status = False

    return status


def __check_unconnected_instance_pins(blocks, reporter):
    """Проверка неподключенных пинов инстансов,
    является приватной"""
    status = True

    for block_name, block in blocks.items():

        #if block.is_primitive:
        #    continue

        for instance_name, instance in block.instances.items():
            for pin_name, pin_ref in instance.interface_pins.items():
                if pin_ref.net is None:
                    report = ReportEntry(
                        error=Error.DISCONNECTED_PIN,
                        message=f"Instance pin '{pin_name}' of '{instance_name}' is not connected to any net",
                        location=f"{block_name}.{instance_name}.{pin_name}"
                    )
                    reporter.add_error(report)
                    status = False

    return status
