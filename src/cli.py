import sys
import argparse
from pathlib import Path
from checker import FileChecker


def main(input: str, output: str):
    if output:
        with open(output, 'w') as output_file:
            checker = FileChecker(input)
            report = checker.check()
            print(report, file=output_file)
    else:
        checker = FileChecker(input)
        report = checker.check()

        print(report.to_dict()["errors"][1])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Netlist Checker')
    parser.add_argument('--input', type=Path, help='Input netlist file')
    parser.add_argument('-o', '--output', type=Path, help='Output report file')

    args = parser.parse_args()
    main(args.input, args.output)

