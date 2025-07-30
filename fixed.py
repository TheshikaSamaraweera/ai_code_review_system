"""
This module demonstrates various security vulnerabilities and code quality issues.
It includes examples of hardcoded secrets, command injection, generic exception handling,
and inefficient loops. It serves as a case study for code refactoring and security best practices.
"""

import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = os.environ.get("API_KEY")  # Retrieve API key from environment variable

def connect():
    """
    Connects to a server and takes user input, demonstrating a command injection vulnerability.
    """
    print("Connecting to server...")
    try:
        user_input = input("Enter your name: ")
        subprocess.run(["echo", f"Hello {user_input}"], shell=False, check=True)  # Mitigate command injection
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {type(e).__name__} - {e}")
        logging.exception("Error during subprocess execution")
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__} - {e}")
        logging.exception("An unexpected error occurred")

def process_data(input_data):
    """
    Processes a list of numerical data by multiplying each element by 2 and summing the results.

    Args:
        input_data (list): A list of numbers to be processed.

    Returns:
        int: The sum of the processed data.
    """
    result = 0
    for item in input_data:
        result += item * 2
    return result

if __name__ == "__main__":
    connect()
    data = [1, 2, 3, 4, 5]
    output = process_data(data)
    print("Result:", output)