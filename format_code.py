#!/usr/bin/env python3
"""Script to format code using Black."""

import subprocess
import sys


def run_black():
    """Run Black formatter on the codebase."""
    try:
        # Run black with check to see what needs formatting
        result = subprocess.run(
            ["black", "--check", "."], capture_output=True, text=True
        )

        if result.returncode != 0:
            print("Files need formatting. Running Black...")
            # Actually format the files
            format_result = subprocess.run(
                ["black", "."], capture_output=True, text=True
            )

            if format_result.returncode == 0:
                print("✅ Code formatted successfully!")
                print(format_result.stdout)
            else:
                print("❌ Error formatting code:")
                print(format_result.stderr)
                return False
        else:
            print("✅ Code is already formatted correctly!")

        return True

    except FileNotFoundError:
        print("❌ Black is not installed. Please install it with:")
        print("pip install black")
        return False
    except Exception as e:
        print(f"❌ Error running Black: {e}")
        return False


if __name__ == "__main__":
    success = run_black()
    sys.exit(0 if success else 1)
