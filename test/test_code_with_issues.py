"""
Test file with intentional bugs and security issues for PR review bot testing.
This file demonstrates the bot's detection capabilities.
"""

import os
import pickle
import subprocess

# SECURITY ISSUE: Hardcoded password
password = "admin123"
api_key = "sk-1234567890abcdef"

# SECURITY ISSUE: Hardcoded database credentials
DB_USER = "root"
DB_PASSWORD = "password123"


def divide_numbers(a, b):
    """BUG: No zero division check"""
    return a / b


def get_user_by_id(user_id):
    """SECURITY ISSUE: SQL Injection vulnerability"""
    query = "SELECT * FROM users WHERE id = " + user_id
    return execute_query(query)


def search_users(name):
    """SECURITY ISSUE: SQL Injection with string formatting"""
    query = "SELECT * FROM users WHERE name = '%s'" % name
    return execute_query(query)


def execute_command(cmd):
    """SECURITY ISSUE: Command injection"""
    os.system(cmd)


def run_shell_command(user_input):
    """SECURITY ISSUE: Shell injection with subprocess"""
    subprocess.call(user_input, shell=True)


def load_data(filename):
    """SECURITY ISSUE: Insecure deserialization"""
    with open(filename, 'rb') as f:
        data = pickle.load(f)
    return data


def hash_password(pwd):
    """SECURITY ISSUE: Weak cryptography"""
    import hashlib
    return hashlib.md5(pwd.encode()).hexdigest()


def process_user_data(user):
    """BUG: Potential null pointer exception"""
    print(user.name)
    print(user.email)
    return user.id


def calculate_average(numbers):
    """BUG: Division by zero if list is empty"""
    return sum(numbers) / len(numbers)


def fetch_url(url):
    """SECURITY ISSUE: SSRF vulnerability"""
    import requests
    response = requests.get(url)
    return response.text


def render_html(user_input):
    """SECURITY ISSUE: XSS vulnerability"""
    html = "<div>" + user_input + "</div>"
    return html


def check_user(username):
    """BUG: Comparison with None using =="""
    if username == None:
        return False
    return True


def process_items(items):
    """BUG: Bare except clause"""
    try:
        for item in items:
            process(item)
    except:
        pass


def debug_function():
    """BUG: Debugger statement left in code"""
    import pdb
    pdb.set_trace()
    return "debugging"


# BUG: Console output in production code
print("Debug: Application started")
print(f"Using password: {password}")


def unsafe_eval(code):
    """SECURITY ISSUE: Code injection via eval"""
    result = eval(code)
    return result


def open_file_unsafe(filepath):
    """BUG: File not closed properly"""
    f = open(filepath, 'r')
    data = f.read()
    return data


def infinite_loop_risk():
    """BUG: Potential infinite loop"""
    while True:
        process_data()
        # Missing break condition


# SECURITY ISSUE: SSL verification disabled
import requests
requests.get('https://api.example.com', verify=False)


# TODO: Fix all these issues before production
# FIXME: Security vulnerabilities need immediate attention
# HACK: Temporary workaround, needs proper solution
