from data import *
from report import *
from loader import *


"""
Некорректная подсхема. Список пинов инстанса подсхемы не соответствует списку пинов блока этой подсхемы.
Неподключённый пин. 1) Неподключённый внешний пин блока. 2) Неподключённый пин инстанса.
"""



def check_subcircuit_correctness(data: Data, reporter: Reporter) -> bool:
    """Функция проверки соответствия списка пинов инстанса подсхемы списку пинов блока этой подсхемы"""
    if Error.PIN_MISMATCH in data.errors_after_parse:
        reporter.add_error(data.errors_after_parse[Error.PIN_MISMATCH])
        return False
    return True


def check_pin_connection(data: Data, reporter: Reporter) -> bool:
    """Функция проверки неподключенных пинов:
    1) Неподключённый внешний пин блока
    2) Неподключённый пин инстанса"""
    status = True

    netlist = data.netlist
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
        if block.is_primitive:
            continue

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
    """Проверка неподключенных пинов инстансов"""
    status = True

    for block_name, block in blocks.items():
        if block.is_primitive:
            continue

        for instance_name, instance in block.instances.items():
            instance_type = instance.type

            for pin_name, pin_ref in instance.interface_pins.items():
                # Находим соответствующий пину инстанса внешний пин в блоке-типе
                corresponding_block_pin = instance_type.interface_pins.get(pin_name)

                # Если соответствующий внешний пин блока-типа подключен,
                # то внутренний пин инстанса считается подключенным автоматически
                if corresponding_block_pin and corresponding_block_pin.net is not None:
                    continue  # Пропускаем проверку - пин считается подключенным

                # Если соответствующий внешний пин не подключен,
                # проверяем подключение самого пина инстанса
                if pin_ref.net is None:
                    report = ReportEntry(
                        error=Error.DISCONNECTED_PIN,
                        message=f"Instance pin '{pin_name}' of '{instance_name}' is not connected to any net",
                        location=f"{block_name}.{instance_name}.{pin_name}"
                    )
                    reporter.add_error(report)
                    status = False

    return status