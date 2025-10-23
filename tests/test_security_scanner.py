"""
Comprehensive tests for SecurityScanner with auto-fix functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.pr-review-bot'))

from analyzers.security_scanner import SecurityScanner


def test_hardcoded_password_detection():
    """Test detection of hardcoded passwords."""
    code = """
password = "mysecretpass123"
api_key = "sk-1234567890abcdef"
"""
    scanner = SecurityScanner()
    issues = scanner.analyze(code, "test.py")
    
    password_issues = [i for i in issues if 'password' in i['message'].lower() or 'key' in i['message'].lower()]
    assert len(password_issues) > 0, "Should detect hardcoded secrets"
    
    # Check for auto-fix
    for issue in password_issues:
        if 'auto_fix' in issue:
            assert 'original' in issue['auto_fix']
            assert 'fixed' in issue['auto_fix']
            assert 'os.getenv' in issue['auto_fix']['fixed'] or 'os.environ' in issue['auto_fix']['fixed']
    
    print("✅ Hardcoded password detection: PASSED")


def test_sql_injection_detection():
    """Test detection of SQL injection vulnerabilities."""
    code = """
query = "SELECT * FROM users WHERE id = %s" % user_id
cursor.execute(f"DELETE FROM posts WHERE id = {post_id}")
"""
    scanner = SecurityScanner()
    issues = scanner.analyze(code, "test.py")
    
    sql_issues = [i for i in issues if 'sql' in i['message'].lower() or 'injection' in i['message'].lower()]
    assert len(sql_issues) > 0, "Should detect SQL injection"
    assert any(i['severity'] == 'critical' for i in sql_issues)
    print("✅ SQL injection detection: PASSED")


def test_xss_detection():
    """Test detection of XSS vulnerabilities."""
    code = """
element.innerHTML = userInput;
const html = dangerouslySetInnerHTML({__html: data});
"""
    scanner = SecurityScanner()
    issues = scanner.analyze(code, "test.js")
    
    xss_issues = [i for i in issues if 'xss' in i['message'].lower() or 'innerHTML' in i['message'].lower()]
    assert len(xss_issues) > 0, "Should detect XSS vulnerabilities"
    
    # Check for auto-fix
    for issue in xss_issues:
        if 'innerHTML' in issue['message']:
            assert 'auto_fix' in issue
            assert 'textContent' in issue['auto_fix']['fixed']
    
    print("✅ XSS detection: PASSED")


def test_weak_crypto_detection():
    """Test detection of weak cryptography."""
    code = """
import hashlib
hash = hashlib.md5(data).hexdigest()
hash2 = hashlib.sha1(password).hexdigest()
"""
    scanner = SecurityScanner()
    issues = scanner.analyze(code, "test.py")
    
    crypto_issues = [i for i in issues if 'md5' in i['message'].lower() or 'sha1' in i['message'].lower() or 'sha-1' in i['message'].lower()]
    assert len(crypto_issues) > 0, "Should detect weak crypto"
    
    # Check for auto-fix
    for issue in crypto_issues:
        if 'auto_fix' in issue:
            assert 'sha256' in issue['auto_fix']['fixed']
    
    print("✅ Weak crypto detection: PASSED")


def test_command_injection_detection():
    """Test detection of command injection."""
    code = """
import os
os.system("rm -rf " + user_input)
subprocess.run(cmd, shell=True)
"""
    scanner = SecurityScanner()
    issues = scanner.analyze(code, "test.py")
    
    cmd_issues = [i for i in issues if 'command' in i['message'].lower() or 'os.system' in i['message'].lower() or 'shell' in i['message'].lower()]
    assert len(cmd_issues) > 0, "Should detect command injection"
    print("✅ Command injection detection: PASSED")


def test_insecure_deserialization():
    """Test detection of insecure deserialization."""
    code = """
import pickle
import yaml
data = pickle.loads(user_data)
config = yaml.load(file_content)
"""
    scanner = SecurityScanner()
    issues = scanner.analyze(code, "test.py")
    
    deser_issues = [i for i in issues if 'pickle' in i['message'].lower() or 'yaml' in i['message'].lower()]
    assert len(deser_issues) > 0, "Should detect insecure deserialization"
    
    # Check for YAML auto-fix
    yaml_issues = [i for i in deser_issues if 'yaml' in i['message'].lower()]
    if yaml_issues:
        assert 'auto_fix' in yaml_issues[0]
        assert 'safe_load' in yaml_issues[0]['auto_fix']['fixed']
    
    print("✅ Insecure deserialization detection: PASSED")


def test_ssl_verification_disabled():
    """Test detection of disabled SSL verification."""
    code = """
response = requests.get(url, verify=False)
"""
    scanner = SecurityScanner()
    issues = scanner.analyze(code, "test.py")
    
    ssl_issues = [i for i in issues if 'ssl' in i['message'].lower() or 'verify' in i['message'].lower()]
    assert len(ssl_issues) > 0, "Should detect disabled SSL verification"
    
    # Check for auto-fix
    if ssl_issues and 'auto_fix' in ssl_issues[0]:
        assert 'verify=True' in ssl_issues[0]['auto_fix']['fixed']
    
    print("✅ SSL verification detection: PASSED")


def test_security_report_generation():
    """Test security report generation."""
    code = """
password = "secret123"
hash = hashlib.md5(data)
"""
    scanner = SecurityScanner()
    issues = scanner.analyze(code, "test.py")
    
    report = scanner.generate_security_report(issues)
    assert len(report) > 0, "Should generate report"
    assert 'Security' in report or 'security' in report
    print("✅ Security report generation: PASSED")


def run_all_tests():
    """Run all security scanner tests."""
    print("\n🔒 Testing Security Scanner...\n")
    
    try:
        test_hardcoded_password_detection()
        test_sql_injection_detection()
        test_xss_detection()
        test_weak_crypto_detection()
        test_command_injection_detection()
        test_insecure_deserialization()
        test_ssl_verification_disabled()
        test_security_report_generation()
        
        print("\n✅ All Security Scanner tests PASSED!\n")
        return True
    except AssertionError as e:
        print(f"\n❌ Test FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
