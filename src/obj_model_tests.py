import pytest
from data import Block, Instance, Pin, PinRef, Net, NetlistProject


@pytest.fixture
def netlist_project():
    """Создание тестового NetlistProject"""
    primitives = {
        "prim1": Block("prim1", is_primitive=True, primitive_pins=["in1", "in2", "out"]),
        "prim2": Block("prim2", is_primitive=True, primitive_pins=["in1", "in3", "out"]),
        "prim3": Block("prim3", is_primitive=True, primitive_pins=["in1", "in2", "out"])
    }
    return NetlistProject("test_project", primitive_blocks=primitives)


@pytest.fixture
def main_block(netlist_project):
    """Создание основного блока"""
    return netlist_project.add_block("main")


class TestNetlistProjectOperations:
    """Тесты операций с NetlistProject"""

    def test_create_empty_project(self):
        """Тест создания пустого проекта"""
        test_nl = NetlistProject("empty_project")
        assert test_nl.blocks == {}
        assert test_nl.name == "empty_project"


class TestBlockOperations:
    """Тесты операций с блоками"""

    def test_add_block(self):
        """Тест создания блоков"""
        test_nl = NetlistProject("empty")
        main1_block = test_nl.add_block("main1")
        main2_block = test_nl.add_block("main2")
        assert main1_block.name == "main1"
        assert main2_block.name == "main2"
        assert set(test_nl.blocks.keys()) == {"main1", "main2"}
        
    def test_add_duplicate_block(self, netlist_project):
        """Тест добавления повторяющегося блока"""
        netlist_project.add_block("main")
        with pytest.raises(Exception, match="main already exists in block test_project"):
            netlist_project.add_block("main")
    
    def test_rename_block(self, netlist_project):
        """Тест переименования блока"""
        netlist_project.add_block("main")
        netlist_project.rename_block("main", "test")
        assert "test" in netlist_project.blocks
        assert "main" not in netlist_project.blocks
    
    def test_remove_block(self, netlist_project):
        """Тест удаления блока"""
        netlist_project.add_block("main")
        netlist_project.remove_block("main")
        assert "main" not in netlist_project.blocks

    def test_add_primitive(self, netlist_project):
        """Тест добавления примитива"""
        prim = netlist_project.add_primitive_block("test_prim", primitive_pins=["in1", "in2", "out"])
        assert set(netlist_project.blocks.keys()) == {"prim1", "prim2", "prim3", "test_prim"}
        assert prim.is_primitive == True
        assert set(prim.interface_pins.keys()) == {"in1", "in2", "out"}

    def test_add_duplicate_primitive(self, netlist_project):
        """Тест добавления повторяющегося примитива"""
        prim = netlist_project.add_primitive_block("test_prim", primitive_pins=["in1", "in2", "out"])
        with pytest.raises(Exception, match="test_prim already exists in block test_project"):
            netlist_project.add_primitive_block("test_prim", primitive_pins=["in1", "in2", "out"])

    def test_remove_primitive(self, netlist_project):
        """Тест удаления примитива"""
        netlist_project.remove_primitive_block("prim1")
        assert "prim1" not in netlist_project.blocks

        

class TestPinOperations:
    """Тесты операций с пинами"""
    
    def test_add_pin(self, netlist_project, main_block):
        """Тест добавления пинов"""
        pin2 = netlist_project.add_pin_to_block("main", "input2")
        pin1 = netlist_project.add_pin_to_block("main", "input1")
        assert pin1.name == "input1"
        assert pin2.name == "input2"
        assert set(main_block.interface_pins.keys()) == {"input1", "input2"}
    
    def test_add_duplicate_pin(self, netlist_project, main_block):
        """Тест добавления повторяющегося пина"""
        netlist_project.add_pin_to_block("main", "input1")
        with pytest.raises(Exception):
            netlist_project.add_pin_to_block("main", "input1")
    
    def test_rename_pin(self, netlist_project, main_block):
        """Тест переименования пина"""
        netlist_project.add_pin_to_block("main", "input1")
        netlist_project.rename_pin_in_block("main", "input1", "clock")

        assert set(main_block.interface_pins.keys()) == {"clock"}        
    
    def test_remove_pin(self, netlist_project, main_block):
        """Тест удаления пина"""
        netlist_project.add_pin_to_block("main", "input1")
        netlist_project.remove_pin_from_block("main", "input1")
        
        assert "input1" not in main_block.interface_pins


class TestInstanceOperations:
    """Тесты операций с инстансами"""
    
    def test_add_instance(self, netlist_project, main_block):
        """Тест добавления инстанса"""
        inst1 = netlist_project.add_instance_to_block("main", "inst1", "prim1")
        inst2 = netlist_project.add_instance_to_block("main", "inst2", "prim2")
        
        assert set(main_block.instances.keys()) == {"inst1", "inst2"}
        assert set(inst1.interface_pins.keys()) == {"in1", "in2", "out"}
        assert set(inst2.interface_pins.keys()) == {"in1", "in3", "out"}
        assert inst1.type.name == "prim1"
        assert inst2.type.name == "prim2"
    
    def test_rename_instance(self, netlist_project, main_block):
        """Тест переименования инстанса"""
        netlist_project.add_instance_to_block("main", "inst1", "prim1")
        netlist_project.rename_instance_in_block("main", "inst1", "inst1_renamed")

        assert set(main_block.instances.keys()) == {"inst1_renamed"}

    def test_remove_instance(self, netlist_project, main_block):
        """Тест удаления инстанса"""
        netlist_project.add_instance_to_block("main", "inst1", "prim1")
        netlist_project.remove_instance_from_block("main", "inst1")
        
        assert set(main_block.instances.keys()) == set()

    def test_add_duplicate_instance(self, netlist_project, main_block):
        """Тест добавления повторяющегося инстанса"""
        netlist_project.add_instance_to_block("main", "inst1", "prim1")
        with pytest.raises(Exception, match="inst1 already exists in block main"):
            netlist_project.add_instance_to_block("main", "inst1", "prim1")

class TestNetOperations:
    """Тесты операций с сетями"""
    
    def test_add_net(self, netlist_project, main_block):
        """Тест добавления сетей"""
        net1 = netlist_project.add_net_to_block("main", "net1")
        net2 = netlist_project.add_net_to_block("main", "net2")
        assert net1.name == "net1"
        assert net2.name == "net2"
        assert set(main_block.nets.keys()) == {"net1", "net2"}
    
    def test_rename_net(self, netlist_project, main_block):
        """Тест переименования сети"""
        netlist_project.add_net_to_block("main", "net1")
        netlist_project.rename_net_in_block("main", "net1", "net_renamed")
        assert set(main_block.nets.keys()) == {"net_renamed"}
        
    
    def test_remove_net(self, netlist_project, main_block):
        """Тест удаления сети"""
        netlist_project.add_net_to_block("main", "net1")
        netlist_project.add_net_to_block("main", "net2")
        netlist_project.remove_net_from_block("main", "net1")
        
        assert set(main_block.nets.keys()) == {"net2"}


class TestConnections:
    """Тесты подключений"""
    
    def test_connect_pins_to_net(self, netlist_project, main_block):
        """Тест подключения пинов к сети"""
        input_pin = netlist_project.add_pin_to_block("main", "input")
        inst1 = netlist_project.add_instance_to_block("main", "inst1", "prim1")
        net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", input_pin)
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["in1"])
        
        assert input_pin.net == net
        assert inst1.interface_pins["in1"].net == net
        assert len(net.pins) == 2
    
    def test_disconnect_pin_from_net(self, netlist_project, main_block):
        """Тест отключения пина от сети"""
        input_pin = netlist_project.add_pin_to_block("main", "input")
        net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", input_pin)
        assert input_pin.net == net
        
        netlist_project.disconnect_pin_from_net_in_block("main", "test_net", "input")
        assert input_pin.net is None
        assert len(net.pins) == 0


class TestPrimitiveBlocks:
    """Тесты примитивных блоков"""
    
    def test_primitive_blocks_exist(self, netlist_project):
        """Тест существования примитивных блоков"""
        assert "prim1" in netlist_project.blocks
        assert "prim2" in netlist_project.blocks
        assert netlist_project.blocks["prim1"].is_primitive
    
    def test_primitive_block_restrictions(self, netlist_project):
        """Тест ограничений для примитивных блоков"""
        prim1_block = netlist_project.blocks["prim1"]
        
        with pytest.raises(Exception, match="Cannot add pin in primitive block prim1"):
            prim1_block.add_interface_pin("new_pin")
        
        with pytest.raises(Exception, match="Cannot add instance in primitive block prim1"):
            prim1_block.add_instance("instance1", prim1_block)
        
        with pytest.raises(Exception, match="Cannot add net in primitive block prim1"):
            prim1_block.add_net("new_net")


class TestPinUpdating:
    """Тесты обновления пинов"""

    def test_pin_updating(self, netlist_project, main_block):
        """Тест обновления пинов при удалении и переименовании"""

        netlist_project.add_block("custom")
        netlist_project.add_pin_to_block("custom", "a")
        netlist_project.add_pin_to_block("custom", "b")
        netlist_project.add_pin_to_block("custom", "c")

        instance = netlist_project.add_instance_to_block("main", "inst1", "custom")
        netlist_project.remove_pin_from_block("custom", "c")     

        netlist_project.rename_pin_in_block("custom", "a", "d")   

        assert set(instance.interface_pins.keys()) == {"d", "b"}
    
    def test_pin_update_after_net_delete(self, netlist_project, main_block):
        """Тест отключения пинов при удалении сети"""
        pin1 = netlist_project.add_pin_to_block("main", "pin1")
        pin2 = netlist_project.add_pin_to_block("main", "pin2")
        test_net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", pin1)
        netlist_project.connect_pin_to_net_in_block("main", "test_net", pin2)
        
        assert pin1.net == test_net
        assert pin2.net == test_net
        
        netlist_project.remove_net_from_block("main", "test_net")
        assert pin1.net is None
        assert pin2.net is None

    
    def test_pin_update_after_instance_delete(self, netlist_project, main_block):
        """Тест отключения пинов инстанса от сети при удалении инстанса"""
        inst1 = netlist_project.add_instance_to_block("main", "inst1", "prim1")
        test_net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["in1"])
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["out"])
        
        assert len(test_net.pins) == 2
        
        netlist_project.remove_instance_from_block("main", "inst1")
        assert len(test_net.pins) == 0


    def test_pin_update_after_primitive_delete(self, netlist_project, main_block):
        """Тест отключения пинов инстанса от сети при удалении примитива"""
        inst1 = netlist_project.add_instance_to_block("main", "inst1", "prim1")
        test_net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["in1"])
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["out"])
        
        assert len(test_net.pins) == 2
        
        netlist_project.remove_instance_from_block("main", "inst1")
        assert len(test_net.pins) == 0



class TestErrorConditions:
    """Тесты обработки ошибок"""
    
    def test_noname_objects(self, netlist_project, main_block):
        """Тест операций с несуществующими объектами"""
        with pytest.raises(Exception):
            netlist_project.remove_block("noname")
        
        with pytest.raises(Exception):
            netlist_project.add_instance_to_block("main", "inst1", "notype")


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    @pytest.fixture
    def edge_case_project(self):
        """Фикстура для тестов граничных случаев"""
        return NetlistProject("edge_case_test")
    
    def test_pin_cannot_be_connected_to_multiple_nets(self, edge_case_project):
        """Тест подключения пина к нескольким сетям одновременно"""
        edge_case_project.add_block("main")
        
        pin = edge_case_project.add_pin_to_block("main", "test_pin")
        net1 = edge_case_project.add_net_to_block("main", "net1")
        net2 = edge_case_project.add_net_to_block("main", "net2")
        
        edge_case_project.connect_pin_to_net_in_block("main", "net1", pin)
        assert pin.net == net1
        
        edge_case_project.connect_pin_to_net_in_block("main", "net2", pin)
        assert pin.net == net2
        assert len(net1.pins) == 1
        assert len(net2.pins) == 0
    