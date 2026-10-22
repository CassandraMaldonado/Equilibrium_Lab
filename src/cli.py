"""Command-line entry point for a reproducible marketplace brief."""

# I use this to rerun the complete analysis from the terminal with a different
# random seed or number of marketplace zones.

import argparse
import json

from .analysis import analyze


def main():
    parser = argparse.ArgumentParser(description="Analyze a marketplace switchback experiment")
    parser.add_argument("--seed", type=int, default=29)
    parser.add_argument("--zones", type=int, default=18)
    args = parser.parse_args()
    print(json.dumps(analyze(args.seed, args.zones), indent=2))


if __name__ == "__main__":
    main()

