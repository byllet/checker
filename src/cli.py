import argparse
from pathlib import Path

from checker import FileChecker


def main(input: str, output: str):
    checker = FileChecker(input)
    report = checker.check()

    if output:
        with open(output, 'w') as output_file:
            print(report, file=output_file)
    else:
        print(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Netlist Checker')
    parser.add_argument('--input', type=Path, help='Input netlist file')
    parser.add_argument('-o', '--output', type=Path, help='Output report file')

    args = parser.parse_args()
    main(args.input, args.output)
