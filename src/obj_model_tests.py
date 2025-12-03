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
    
    def test_add_block_with_primitive_name(self, netlist_project):
        """Тест создания блока с именем примитива"""
        with pytest.raises(Exception, match="prim1 already exists"):
            netlist_project.add_block("prim1")
        
        # Создание нового блока
        netlist_project.add_block("main")
        assert "main" in netlist_project.blocks


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
    
    def test_rename_block_to_existing_name(self, netlist_project):
        """Тест переименования блока на существующее имя"""
        netlist_project.add_block("block1")
        netlist_project.add_block("block2")
        
        with pytest.raises(Exception, match="block2 already exists"):
            netlist_project.rename_block("block1", "block2")
    
    def test_remove_block(self, netlist_project):
        """Тест удаления блока"""
        netlist_project.add_block("main")
        netlist_project.remove_block("main")
        assert "main" not in netlist_project.blocks
    
    def test_remove_nonexistent_block(self, netlist_project):
        """Тест удаления несуществующего блока"""

        with pytest.raises(Exception):
            netlist_project.remove_block("nonexistent")

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
    
    def test_add_primitive_with_mismatched_name(self, netlist_project):
        """Тест добавления примитива с именем, не совпадающим с ключом"""
        prim = netlist_project.add_primitive_block("test_prim", primitive_pins=["in1", "in2", "out"])
        assert "test_prim" in netlist_project.blocks
        assert prim.name == "test_prim"
        assert netlist_project.blocks["test_prim"].name == "test_prim"

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
    
    def test_rename_pin_to_existing_name(self, netlist_project, main_block):
        """Тест переименования пина на существующее имя"""
        netlist_project.add_pin_to_block("main", "pin1")
        netlist_project.add_pin_to_block("main", "pin2")
        
        with pytest.raises(Exception, match="already exists"):
            netlist_project.rename_pin_in_block("main", "pin1", "pin2")
    
    def test_remove_pin(self, netlist_project, main_block):
        """Тест удаления пина"""
        netlist_project.add_pin_to_block("main", "input1")
        netlist_project.remove_pin_from_block("main", "input1")
        
        assert "input1" not in main_block.interface_pins
    
    def test_remove_pin_connected_to_net(self, netlist_project, main_block):
        """Тест удаления пина, подключенного к сети"""
        pin = netlist_project.add_pin_to_block("main", "input1")
        net = netlist_project.add_net_to_block("main", "net1")
        
        netlist_project.connect_pin_to_net_in_block("main", "net1", pin)
        assert pin.net == net
        
        netlist_project.remove_pin_from_block("main", "input1")
        assert "input1" not in main_block.interface_pins
        # Проверяем, что пин был отключен от сети
        assert len(net.pins) == 0


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
    
    def test_rename_instance_to_existing_name(self, netlist_project, main_block):
        """Тест переименования инстанса на существующее имя"""
        netlist_project.add_instance_to_block("main", "inst1", "prim1")
        netlist_project.add_instance_to_block("main", "inst2", "prim2")
        
        with pytest.raises(Exception, match="already exists"):
            netlist_project.rename_instance_in_block("main", "inst1", "inst2")

    def test_remove_instance(self, netlist_project, main_block):
        """Тест удаления инстанса"""
        netlist_project.add_instance_to_block("main", "inst1", "prim1")
        netlist_project.remove_instance_from_block("main", "inst1")
        
        assert set(main_block.instances.keys()) == set()
    
    def test_remove_instance_connected_to_nets(self, netlist_project, main_block):
        """Тест удаления инстанса, подключенного к сетям"""
        inst1 = netlist_project.add_instance_to_block("main", "inst1", "prim1")
        net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["in1"])
        assert len(net.pins) == 1
        
        netlist_project.remove_instance_from_block("main", "inst1")
        assert "inst1" not in main_block.instances
        assert len(net.pins) == 0

    def test_add_duplicate_instance(self, netlist_project, main_block):
        """Тест добавления повторяющегося инстанса"""
        netlist_project.add_instance_to_block("main", "inst1", "prim1")
        with pytest.raises(Exception, match="inst1 already exists in block main"):
            netlist_project.add_instance_to_block("main", "inst1", "prim1")
    
    def test_add_instance_with_nonexistent_type(self, netlist_project, main_block):
        """Тест добавления инстанса с несуществующим типом"""
        with pytest.raises(Exception):
            netlist_project.add_instance_to_block("main", "inst1", "nonexistent")


class TestNetOperations:
    """Тесты операций с сетями"""
    
    def test_add_net(self, netlist_project, main_block):
        """Тест добавления сетей"""
        net1 = netlist_project.add_net_to_block("main", "net1")
        net2 = netlist_project.add_net_to_block("main", "net2")
        assert net1.name == "net1"
        assert net2.name == "net2"
        assert set(main_block.nets.keys()) == {"net1", "net2"}
    
    def test_add_duplicate_net(self, netlist_project, main_block):
        """Тест добавления повторяющейся сети"""
        netlist_project.add_net_to_block("main", "net1")
        with pytest.raises(Exception, match="net1 already exists in block main"):
            netlist_project.add_net_to_block("main", "net1")
    
    def test_rename_net(self, netlist_project, main_block):
        """Тест переименования сети"""
        netlist_project.add_net_to_block("main", "net1")
        netlist_project.rename_net_in_block("main", "net1", "net_renamed")
        assert set(main_block.nets.keys()) == {"net_renamed"}
    
    def test_rename_net_to_existing_name(self, netlist_project, main_block):
        """Тест переименования сети на существующее имя"""
        netlist_project.add_net_to_block("main", "net1")
        netlist_project.add_net_to_block("main", "net2")
        
        with pytest.raises(Exception):
            netlist_project.rename_net_in_block("main", "net1", "net2")
    
    def test_rename_net_updates_pins_references(self, netlist_project, main_block):
        """Тест обновления ссылок на сеть при переименовании"""
        net = netlist_project.add_net_to_block("main", "old_net")
        pin = netlist_project.add_pin_to_block("main", "pin1")
        
        netlist_project.connect_pin_to_net_in_block("main", "old_net", pin)
        assert pin.net == net
        
        netlist_project.rename_net_in_block("main", "old_net", "new_net")
        assert pin.net.name == "new_net"
    
    def test_remove_net(self, netlist_project, main_block):
        """Тест удаления сети"""
        netlist_project.add_net_to_block("main", "net1")
        netlist_project.add_net_to_block("main", "net2")
        netlist_project.remove_net_from_block("main", "net1")
        
        assert set(main_block.nets.keys()) == {"net2"}
    
    def test_remove_net_with_connected_pins(self, netlist_project, main_block):
        """Тест удаления сети с подключенными пинами"""
        pin = netlist_project.add_pin_to_block("main", "pin1")
        net = netlist_project.add_net_to_block("main", "net1")
        
        netlist_project.connect_pin_to_net_in_block("main", "net1", pin)
        assert pin.net == net
        
        netlist_project.remove_net_from_block("main", "net1")
        assert "net1" not in main_block.nets
        assert pin.net is None


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
    
    def test_pin_update_after_primitive_delete(self, netlist_project, main_block):
        """Тест отключения пинов инстанса от сети при удалении примитива"""
        inst1 = netlist_project.add_instance_to_block("main", "inst1", "prim1")
        test_net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["in1"])
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["out"])
        
        assert len(test_net.pins) == 2
        
        netlist_project.remove_block("prim1")

        assert len(test_net.pins) == 0

    def test_pin_update_after_block_delete(self, netlist_project, main_block):
        """Тест отключения пинов инстанса от сети при удалении блока"""
        custom1 = netlist_project.add_block("custom")
        pin1 = netlist_project.add_pin_to_block("custom", "in1")
        pin2 = netlist_project.add_pin_to_block("custom", "out")
        inst1 = netlist_project.add_instance_to_block("main", "inst1", "custom")
        
        test_net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["in1"])
        netlist_project.connect_pin_to_net_in_block("main", "test_net", inst1.interface_pins["out"])
        netlist_project.add_instance_to_block("custom", "test1", "prim1")
        netlist_project.remove_primitive_block("prim1")
        
        assert len(test_net.pins) == 2
        
        netlist_project.remove_block("custom")
        
        assert len(test_net.pins) == 0



    def test_connect_nonexistent_pin_to_net(self, netlist_project, main_block):
        """Тест подключения несуществующего пина к сети"""
        net = netlist_project.add_net_to_block("main", "test_net")
        
        # Создаем фиктивный пин, который не принадлежит блоку
        fake_pin = Pin("fake_pin", None)
        
        with pytest.raises(Exception):
            netlist_project.connect_pin_to_net_in_block("main", "test_net", fake_pin)
    
    def test_disconnect_pin_from_net(self, netlist_project, main_block):
        """Тест отключения пина от сети"""
        input_pin = netlist_project.add_pin_to_block("main", "input")
        net = netlist_project.add_net_to_block("main", "test_net")
        
        netlist_project.connect_pin_to_net_in_block("main", "test_net", input_pin)
        assert input_pin.net == net
        
        netlist_project.disconnect_pin_from_net_in_block("main", "test_net", "input")
        assert input_pin.net is None
        assert len(net.pins) == 0
    
    def test_disconnect_nonexistent_pin(self, netlist_project, main_block):
        """Тест отключения несуществующего пина от сети"""
        net = netlist_project.add_net_to_block("main", "test_net")
        
        with pytest.raises(Exception):
            netlist_project.disconnect_pin_from_net_in_block("main", "test_net", "nonexistent")


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
    
    def test_pin_updating_in_multiple_instances(self, netlist_project, main_block):
        """Тест обновления пинов во множестве инстансов"""
        netlist_project.add_block("custom")
        netlist_project.add_pin_to_block("custom", "a")
        netlist_project.add_pin_to_block("custom", "b")
        netlist_project.add_pin_to_block("custom", "c")

        inst1 = netlist_project.add_instance_to_block("main", "inst1", "custom")
        inst2 = netlist_project.add_instance_to_block("main", "inst2", "custom")
        inst3 = netlist_project.add_instance_to_block("main", "inst3", "custom")


        netlist_project.remove_pin_from_block("custom", "c")
        netlist_project.rename_pin_in_block("custom", "a", "d")

        # Проверяем, что все инстансы обновились
        for inst in [inst1, inst2, inst3]:
            assert set(inst.interface_pins.keys()) == {"d", "b"}
    
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
    

class TestUpdates:
    """Тесты комплексного обновления при изменении типов"""
    
    def test_instance_update_after_pin_renaming_in_type(self, netlist_project, main_block):
        """Тест обновления инстанса при переименовании пинов в типе"""
        netlist_project.add_block("custom_block")
        netlist_project.add_pin_to_block("custom_block", "old_pin1")
        netlist_project.add_pin_to_block("custom_block", "old_pin2")
        
        instance = netlist_project.add_instance_to_block("main", "inst1", "custom_block")
        assert "old_pin1" in instance.interface_pins
        assert "old_pin2" in instance.interface_pins
        
        net1 = netlist_project.add_net_to_block("main", "net1")
        net2 = netlist_project.add_net_to_block("main", "net2")
        netlist_project.connect_pin_to_net_in_block("main", "net1", instance.interface_pins["old_pin1"])
        netlist_project.connect_pin_to_net_in_block("main", "net2", instance.interface_pins["old_pin2"])
        

        netlist_project.rename_pin_in_block("custom_block", "old_pin1", "new_pin1")
        netlist_project.rename_pin_in_block("custom_block", "old_pin2", "new_pin2")
        
        assert "new_pin1" in instance.interface_pins
        assert "new_pin2" in instance.interface_pins
        assert "old_pin1" not in instance.interface_pins
        assert "old_pin2" not in instance.interface_pins
        
        assert instance.interface_pins["new_pin1"].net == net1
        assert instance.interface_pins["new_pin2"].net == net2


class TestErrorConditions:
    """Тесты обработки ошибок"""
    
    def test_nonexistent_objects(self, netlist_project, main_block):
        """Тест операций с несуществующими объектами"""
        with pytest.raises(Exception):
            netlist_project.remove_block("noname")
        
        with pytest.raises(Exception):
            netlist_project.add_instance_to_block("main", "inst1", "notype")
    
    def test_invalid_operations_on_nonexistent_blocks(self, netlist_project):
        """Тест операций на несуществующих блоках"""
        with pytest.raises(Exception):
            netlist_project.add_pin_to_block("nonexistent", "pin1")
        
        with pytest.raises(Exception):
            netlist_project.add_instance_to_block("nonexistent", "inst1", "prim1")
        
        with pytest.raises(Exception):
            netlist_project.add_net_to_block("nonexistent", "net1")


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    @pytest.fixture
    def edge_case_project(self):
        return NetlistProject("edge_case_test")
    
    def test_mass_operations(self, edge_case_project):
        """Тест массовых операций с большим количеством объектов"""
        edge_case_project.add_block("main")
        
        for i in range(100):
            edge_case_project.add_pin_to_block("main", f"pin_{i}")
        
        for i in range(50):
            edge_case_project.add_net_to_block("main", f"net_{i}")
        
        edge_case_project.add_primitive_block("simple_gate", primitive_pins=["in", "out"])
        for i in range(100):
            edge_case_project.add_instance_to_block("main", f"gate_{i}", "simple_gate")
        
        main_block = edge_case_project.blocks["main"]
        assert len(main_block.interface_pins) == 100
        assert len(main_block.nets) == 50
        assert len(main_block.instances) == 100