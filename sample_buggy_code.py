"""
Sample code with intentional bugs for testing PR review bot
"""

# Security Issue: Hardcoded API key
API_KEY = "sk-test-hardcoded-key-12345"

# Bug: Division by zero
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count  # What if numbers is empty?

# Security Issue: SQL Injection
def get_user_by_id(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    return execute_query(query)

# Bug: Null pointer
def print_user_name(user):
    print(user.name)  # What if user is None?

# Code Quality: Bare except
def risky_function():
    try:
        do_something()
    except:  # Catches everything
        pass

# Security Issue: Weak crypto
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# Bug: Resource leak
def read_config(filename):
    f = open(filename, 'r')
    data = f.read()
    return data  # File never closed

# Code Quality: Wrong comparison
def check_none(value):
    if value == None:  # Should use 'is None'
        return True
    return False

# Debug code left in
def process_data(data):
    print(f"Debug: {data}")
    import pdb; pdb.set_trace()
    return data.upper()
