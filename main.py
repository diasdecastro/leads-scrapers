#!/usr/bin/env python3
"""
Main entry point for the leads scraper project.
This file delegates to the main CLI interface.
"""

import subprocess
import sys
import os


def main():
    script_dir = os.path.dirname(__file__)
    cli_path = os.path.join(script_dir, "cli.py")

    cmd = [sys.executable, cli_path] + sys.argv[1:]

    try:
        result = subprocess.run(cmd, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
