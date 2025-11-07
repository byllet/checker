import sys
import argparse
from pathlib import Path
from checker import Checker

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Netlist Checker')
    parser.add_argument('--input', type=Path, help='Input netlist file')
    parser.add_argument('-o', '--output', type=Path, help='Output report file')

    args = parser.parse_args()
    input = args.input

    output = sys.stdout
    if args.output:
        pass

    checker = Checker(input)
    report = checker.check()

    print(report, file=output)
