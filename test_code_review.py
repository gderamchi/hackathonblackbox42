"""
Test file with intentional issues for PR review bot testing.
This file contains various bugs, security issues, and code quality problems.
"""

import os
import pickle
import hashlib

# Security Issue 1: Hardcoded credentials
API_KEY = "sk-test123456789abcdef"
PASSWORD = "admin123"
SECRET_TOKEN = "my-secret-token-12345"

# Security Issue 2: SQL Injection vulnerability
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)

# Security Issue 3: Weak cryptography
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Bug 1: Division by zero
def calculate_average(total, count):
    return total / count  # What if count is 0?

# Bug 2: Null pointer exception
def get_user_name(user):
    return user.name  # What if user is None?

# Bug 3: Infinite loop
def process_items(items):
    while True:
        for item in items:
            print(item)
        # Missing break statement!

# Bug 4: Resource leak
def read_file(filename):
    f = open(filename, 'r')
    data = f.read()
    return data  # File never closed!

# Code Quality Issue 1: Bare except
def risky_operation():
    try:
        dangerous_function()
    except:  # Catches everything including SystemExit
        pass

# Code Quality Issue 2: Wrong comparison
def check_value(value):
    if value == None:  # Should use 'is None'
        return False
    return True

# Code Quality Issue 3: Debug code left in
def process_data(data):
    print(f"Debug: processing {data}")  # Remove before commit
    import pdb; pdb.set_trace()  # Debugger left in!
    return data.upper()

# Security Issue 4: Command injection
def run_command(user_input):
    os.system(f"ls {user_input}")  # Command injection risk!

# Security Issue 5: Insecure deserialization
def load_data(data):
    return pickle.loads(data)  # Arbitrary code execution risk!

# Bug 5: Type error
def concatenate(a, b):
    return a + b  # What if a is int and b is str?

# Code Quality Issue 4: Unused variable
def calculate_total(items):
    total = 0
    count = 0  # Never used
    for item in items:
        total += item
    return total

# Security Issue 6: Information disclosure
def login(username, password):
    print(f"Login attempt: {username} / {password}")  # Logging sensitive data!
    if username == "admin" and password == PASSWORD:
        return True
    return False

# Bug 6: Index out of range
def get_first_item(items):
    return items[0]  # What if items is empty?

# Code Quality Issue 5: Complex nested logic
def complex_function(a, b, c, d):
    if a:
        if b:
            if c:
                if d:
                    return True
    return False

# Main execution
if __name__ == "__main__":
    # This will trigger multiple issues
    user_id = input("Enter user ID: ")
    user = get_user(user_id)  # SQL injection
    print(get_user_name(user))  # Potential null pointer
    
    result = calculate_average(100, 0)  # Division by zero
    print(f"Average: {result}")
