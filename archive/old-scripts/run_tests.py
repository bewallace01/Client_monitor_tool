#!/usr/bin/env python
"""
Test Runner Script for Client Intelligence Monitor

Provides convenient commands for running different test suites.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list[str], description: str) -> int:
    """Run a command and return the exit code."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for Client Intelligence Monitor"
    )

    parser.add_argument(
        "suite",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "fast", "slow", "coverage"],
        help="Test suite to run (default: all)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "-f", "--file",
        help="Run specific test file"
    )

    parser.add_argument(
        "-k", "--keyword",
        help="Run tests matching keyword"
    )

    args = parser.parse_args()

    # Base pytest command
    pytest_cmd = ["pytest"]

    if args.verbose:
        pytest_cmd.append("-v")

    # Handle different test suites
    if args.suite == "all":
        description = "Running all tests"

    elif args.suite == "unit":
        pytest_cmd.extend(["-m", "unit"])
        description = "Running unit tests only"

    elif args.suite == "integration":
        pytest_cmd.extend(["-m", "integration"])
        description = "Running integration tests only"

    elif args.suite == "fast":
        pytest_cmd.extend(["-m", "not slow"])
        description = "Running fast tests only (excluding slow tests)"

    elif args.suite == "slow":
        pytest_cmd.extend(["-m", "slow"])
        description = "Running slow tests only"

    elif args.suite == "coverage":
        pytest_cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=70"
        ])
        description = "Running tests with coverage report"

    # Add specific file if provided
    if args.file:
        pytest_cmd.append(args.file)
        description += f" (file: {args.file})"

    # Add keyword filter if provided
    if args.keyword:
        pytest_cmd.extend(["-k", args.keyword])
        description += f" (keyword: {args.keyword})"

    # Run the tests
    exit_code = run_command(pytest_cmd, description)

    # Print summary
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*60}\n")

    # Open coverage report if generated
    if args.suite == "coverage" and exit_code == 0:
        coverage_file = Path("htmlcov/index.html")
        if coverage_file.exists():
            print(f"\n📊 Coverage report generated: {coverage_file}")
            print("   Open in browser to view detailed coverage report\n")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
