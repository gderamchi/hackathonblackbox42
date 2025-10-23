"""
Comprehensive tests for BugDetector with auto-fix functionality.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.pr-review-bot'))

from analyzers.bug_detector import BugDetector


def test_bare_except_detection():
    """Test detection of bare except clauses."""
    code = """
try:
    risky_operation()
except:
    pass
"""
    detector = BugDetector()
    issues = detector.analyze(code, "test.py")
    
    assert len(issues) > 0, "Should detect bare except"
    issue = [i for i in issues if 'except' in i['message'].lower()][0]
    assert issue['severity'] == 'medium'
    assert 'auto_fix' in issue
    print("✅ Bare except detection: PASSED")


def test_none_comparison_detection():
    """Test detection of == None comparisons."""
    code = """
if user == None:
    return False
"""
    detector = BugDetector()
    issues = detector.analyze(code, "test.py")
    
    none_issues = [i for i in issues if 'None' in i['message']]
    assert len(none_issues) > 0, "Should detect == None"
    assert none_issues[0]['auto_fix'] is not None
    print("✅ None comparison detection: PASSED")


def test_debugger_detection():
    """Test detection of debugger statements."""
    code = """
import pdb
pdb.set_trace()
print("debug")
"""
    detector = BugDetector()
    issues = detector.analyze(code, "test.py")
    
    debug_issues = [i for i in issues if 'debugger' in i['message'].lower() or 'pdb' in i['message'].lower()]
    assert len(debug_issues) > 0, "Should detect pdb"
    print("✅ Debugger detection: PASSED")


def test_javascript_patterns():
    """Test JavaScript-specific patterns."""
    code = """
var x = 5;
if (a == b) {
    console.log("test");
}
debugger;
"""
    detector = BugDetector()
    issues = detector.analyze(code, "test.js")
    
    assert len(issues) > 0, "Should detect JS issues"
    
    # Check for var detection
    var_issues = [i for i in issues if 'var' in i['message'].lower()]
    assert len(var_issues) > 0, "Should detect var usage"
    
    # Check for == detection
    equality_issues = [i for i in issues if '==' in i['message'] or 'equality' in i['message'].lower()]
    assert len(equality_issues) > 0, "Should detect =="
    
    print("✅ JavaScript patterns: PASSED")


def test_auto_fix_generation():
    """Test auto-fix code generation."""
    code = """
try:
    operation()
except:
    pass
"""
    detector = BugDetector()
    issues = detector.analyze(code, "test.py")
    
    issue = [i for i in issues if 'except' in i['message'].lower()][0]
    assert 'auto_fix' in issue, "Should have auto_fix"
    assert 'original' in issue['auto_fix'], "Should have original code"
    assert 'fixed' in issue['auto_fix'], "Should have fixed code"
    assert 'except:' in issue['auto_fix']['original']
    assert 'except Exception:' in issue['auto_fix']['fixed']
    print("✅ Auto-fix generation: PASSED")


def test_complexity_check():
    """Test complexity metrics calculation."""
    code = """
def complex_function():
    for i in range(10):
        for j in range(10):
            if i > j:
                print(i, j)
"""
    detector = BugDetector()
    metrics = detector.check_complexity(code)
    
    assert 'total_lines' in metrics
    assert 'code_lines' in metrics
    assert 'max_nesting_depth' in metrics
    assert metrics['max_nesting_depth'] > 0
    print("✅ Complexity check: PASSED")


def run_all_tests():
    """Run all bug detector tests."""
    print("\n🧪 Testing Bug Detector...\n")
    
    try:
        test_bare_except_detection()
        test_none_comparison_detection()
        test_debugger_detection()
        test_javascript_patterns()
        test_auto_fix_generation()
        test_complexity_check()
        
        print("\n✅ All Bug Detector tests PASSED!\n")
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
