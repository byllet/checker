from syntax_check import check_syntax
from network_check import check_network_connection, check_network_correctness
from hierarchy_loop_and_incompletence_check import check_cycle_hierarchy, check_incomplete_hierarchy
from scheme_check import check_pin_connection, check_subcircuit_correctness


STRATEGIES_FILE = [check_syntax, 
                   check_incomplete_hierarchy,
                   check_cycle_hierarchy,
                   check_pin_connection,
                   check_subcircuit_correctness,
                   check_network_correctness, 
                   check_network_connection]

STRATEGIES_NETLIST = STRATEGIES_FILE
