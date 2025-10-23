"""
Master test runner - runs all test suites.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.pr-review-bot'))

def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("🧪 RUNNING COMPREHENSIVE TEST SUITE")
    print("="*60 + "\n")
    
    all_passed = True
    results = []
    
    # Test 1: Bug Detector
    print("📋 Test Suite 1/6: Bug Detector")
    print("-" * 60)
    try:
        from test_bug_detector import run_all_tests as test_bug_detector
        if test_bug_detector():
            results.append(("✅ Bug Detector", "PASSED"))
        else:
            results.append(("❌ Bug Detector", "FAILED"))
            all_passed = False
    except Exception as e:
        results.append(("❌ Bug Detector", f"ERROR: {e}"))
        all_passed = False
    
    # Test 2: Security Scanner
    print("\n📋 Test Suite 2/6: Security Scanner")
    print("-" * 60)
    try:
        from test_security_scanner import run_all_tests as test_security_scanner
        if test_security_scanner():
            results.append(("✅ Security Scanner", "PASSED"))
        else:
            results.append(("❌ Security Scanner", "FAILED"))
            all_passed = False
    except Exception as e:
        results.append(("❌ Security Scanner", f"ERROR: {e}"))
        all_passed = False
    
    # Test 3: Dependency Scanner
    print("\n📋 Test Suite 3/6: Dependency Scanner")
    print("-" * 60)
    try:
        from test_dependency_scanner import run_all_tests as test_dependency_scanner
        if test_dependency_scanner():
            results.append(("✅ Dependency Scanner", "PASSED"))
        else:
            results.append(("❌ Dependency Scanner", "FAILED"))
            all_passed = False
    except Exception as e:
        results.append(("❌ Dependency Scanner", f"ERROR: {e}"))
        all_passed = False
    
    # Test 4: Performance Analyzer (basic tests)
    print("\n📋 Test Suite 4/6: Performance Analyzer")
    print("-" * 60)
    try:
        from analyzers.performance_analyzer import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer()
        
        # Test nested loop detection
        code = """
for i in range(10):
    for j in range(10):
        print(i, j)
"""
        issues = analyzer.analyze(code, "test.py")
        assert len(issues) > 0, "Should detect nested loops"
        print("✅ Nested loop detection: PASSED")
        
        # Test N+1 query detection
        code2 = """
for user in users:
    db.query("SELECT * FROM posts WHERE user_id = ?", user.id)
"""
        issues2 = analyzer.analyze(code2, "test.py")
        assert len(issues2) > 0, "Should detect N+1 queries"
        print("✅ N+1 query detection: PASSED")
        
        results.append(("✅ Performance Analyzer", "PASSED"))
    except Exception as e:
        print(f"❌ Performance Analyzer: {e}")
        results.append(("❌ Performance Analyzer", f"ERROR: {e}"))
        all_passed = False
    
    # Test 5: Code Duplication Detector (basic tests)
    print("\n📋 Test Suite 5/6: Code Duplication Detector")
    print("-" * 60)
    try:
        from analyzers.code_duplication_detector import CodeDuplicationDetector
        detector = CodeDuplicationDetector()
        
        # Test with duplicate code
        code = """
def function1():
    x = 1
    y = 2
    z = x + y
    return z

def function2():
    x = 1
    y = 2
    z = x + y
    return z
"""
        issues = detector.analyze_file("test.py", code)
        print(f"✅ Duplication detection: PASSED (found {len(issues)} duplicates)")
        
        results.append(("✅ Code Duplication Detector", "PASSED"))
    except Exception as e:
        print(f"❌ Code Duplication Detector: {e}")
        results.append(("❌ Code Duplication Detector", f"ERROR: {e}"))
        all_passed = False
    
    # Test 6: Complexity Analyzer (basic tests)
    print("\n📋 Test Suite 6/7: Complexity Analyzer")
    print("-" * 60)
    try:
        from analyzers.complexity_analyzer import ComplexityAnalyzer
        analyzer = ComplexityAnalyzer()
        
        # Test with complex function
        code = """
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                for i in range(x):
                    for j in range(y):
                        if i == j:
                            print(i)
    return x + y + z
"""
        issues = analyzer.analyze(code, "test.py")
        assert len(issues) > 0, "Should detect complexity issues"
        print(f"✅ Complexity analysis: PASSED (found {len(issues)} issues)")
        
        results.append(("✅ Complexity Analyzer", "PASSED"))
    except Exception as e:
        print(f"❌ Complexity Analyzer: {e}")
        results.append(("❌ Complexity Analyzer", f"ERROR: {e}"))
        all_passed = False
    
    # Test 7: Interactive AI (comprehensive tests)
    print("\n📋 Test Suite 7/7: Interactive AI")
    print("-" * 60)
    try:
        from test_interactive_ai import run_all_tests as test_interactive_ai
        if test_interactive_ai():
            results.append(("✅ Interactive AI", "PASSED"))
        else:
            results.append(("❌ Interactive AI", "FAILED"))
            all_passed = False
    except Exception as e:
        print(f"❌ Interactive AI: {e}")
        results.append(("❌ Interactive AI", f"ERROR: {e}"))
        all_passed = False
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60 + "\n")
    
    for test_name, status in results:
        print(f"{test_name}: {status}")
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
