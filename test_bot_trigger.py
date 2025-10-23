"""
Simple test file to trigger the PR review bot.
This file contains intentional issues for the bot to detect.
"""

# SECURITY ISSUE: Hardcoded password
password = "MySecretPassword123"

# BUG: Division by zero risk
def calculate(a, b):
    return a / b  # No zero check!

# QUALITY: Using == None
def check_value(value):
    if value == None:  # Should use 'is None'
        return False
    return True

print("This file will trigger the bot!")
