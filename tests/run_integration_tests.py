"""Integration test runner for SpecOps."""

import sys
import subprocess
from pathlib import Path
import argparse


def run_integration_tests(test_pattern: str = None, verbose: bool = False, coverage: bool = False):
    """Run integration tests with optional filtering and coverage."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add integration test directory
    test_dir = Path(__file__).parent / "integration"
    cmd.append(str(test_dir))
    
    # Add test pattern if specified
    if test_pattern:
        cmd.extend(["-k", test_pattern])
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    # Add other useful flags
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "-x",  # Stop on first failure
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)
    
    # Run the tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run SpecOps integration tests")
    
    parser.add_argument(
        "-k", "--pattern",
        help="Run tests matching the given pattern"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    
    parser.add_argument(
        "--end-to-end",
        action="store_true",
        help="Run only end-to-end workflow tests"
    )
    
    parser.add_argument(
        "--hooks",
        action="store_true",
        help="Run only hook integration tests"
    )
    
    parser.add_argument(
        "--file-ops",
        action="store_true",
        help="Run only file operations tests"
    )
    
    parser.add_argument(
        "--sample-repos",
        action="store_true",
        help="Run only sample repository tests"
    )
    
    args = parser.parse_args()
    
    # Determine test pattern based on flags
    pattern = args.pattern
    
    if args.end_to_end:
        pattern = "test_end_to_end_workflow"
    elif args.hooks:
        pattern = "test_hook_integration"
    elif args.file_ops:
        pattern = "test_file_operations"
    elif args.sample_repos:
        pattern = "test_sample_repository"
    
    # Run the tests
    exit_code = run_integration_tests(
        test_pattern=pattern,
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    # Print summary
    if exit_code == 0:
        print("\n" + "=" * 50)
        print("✅ All integration tests passed!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Some integration tests failed!")
        print("=" * 50)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()