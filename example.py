# example.py

import os
import sys

API_KEY = "123456"  # 🚨 Hardcoded secret

def connect():
    print("Connecting to server...")
    try:
        user_input = input("Enter your name: ")
        os.system(f"echo Hello {user_input}")  # 🚨 Vulnerable to command injection
    except Exception as e:
        print("An error occurred")  # 🔧 No exception detail shown

def process_data(data):
    result = 0
    for i in range(len(data)):
        result += data[i] * 2
    return result

if __name__ == "__main__":
    connect()
    data = [1, 2, 3, 4, 5]
    output = process_data(data)
    print("Result:", output)
