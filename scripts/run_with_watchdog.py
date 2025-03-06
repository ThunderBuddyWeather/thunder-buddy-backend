#!/usr/bin/env python
"""
Watchdog script for Flask application
This script runs the Flask application and restarts it if it crashes due to syntax errors
"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("watchdog")

# Get the root directory of the project
ROOT_DIR = Path(__file__).parent.parent


def run_flask_app() -> bool:
    """Run the Flask application and monitor for errors"""
    logger.info("Starting Flask application...")

    flask_cmd = [sys.executable, "run.py"]
    env = os.environ.copy()

    try:
        # Start the Flask application
        process = subprocess.Popen(
            flask_cmd,
            cwd=ROOT_DIR,
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr
        )

        # Wait for the process to complete
        return_code = process.wait()

        if return_code != 0:
            logger.error(f"Flask application exited with code {return_code}")
            return False

        return True

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, stopping Flask application...")
        if 'process' in locals():
            process.terminate()
        return False

    except Exception as e:
        logger.error(f"Error running Flask application: {e}")
        return False


def main() -> None:
    """Main watchdog loop"""
    logger.info("Starting watchdog for Flask application...")

    # Retry settings
    max_retries = 10
    retry_count = 0
    retry_delay = 2  # seconds

    while retry_count < max_retries:
        success = run_flask_app()

        if success:
            logger.info("Flask application exited cleanly")
            break

        retry_count += 1
        if retry_count < max_retries:
            logger.info(f"Restarting Flask application in {retry_delay} seconds (attempt {retry_count}/{max_retries})...")
            time.sleep(retry_delay)
        else:
            logger.error(f"Maximum retry attempts ({max_retries}) reached, giving up")

    logger.info("Watchdog exiting")


if __name__ == "__main__":
    main()
