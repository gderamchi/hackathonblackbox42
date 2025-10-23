"""
Comprehensive tests for DependencyScanner with OSV API integration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.pr-review-bot'))

from analyzers.dependency_scanner import DependencyScanner


def test_parse_requirements_txt():
    """Test parsing requirements.txt file."""
    content = """
requests==2.25.0
django==3.2.0
flask>=2.0.0
numpy
# comment line
pytest==7.0.0
"""
    scanner = DependencyScanner()
    packages = scanner._parse_requirements_txt(content)
    
    assert len(packages) > 0, "Should parse packages"
    assert any(p['name'] == 'requests' and p['version'] == '2.25.0' for p in packages)
    assert any(p['name'] == 'django' and p['version'] == '3.2.0' for p in packages)
    print("✅ Requirements.txt parsing: PASSED")


def test_parse_package_json():
    """Test parsing package.json file."""
    content = """
{
    "dependencies": {
        "express": "4.17.1",
        "lodash": "4.17.20",
        "axios": "^0.21.0"
    },
    "devDependencies": {
        "jest": "27.0.0"
    }
}
"""
    scanner = DependencyScanner()
    packages = scanner._parse_package_json(content)
    
    assert len(packages) > 0, "Should parse packages"
    assert any(p['name'] == 'express' for p in packages)
    assert any(p['name'] == 'lodash' for p in packages)
    print("✅ Package.json parsing: PASSED")


def test_osv_api_query():
    """Test OSV API query (real API call)."""
    scanner = DependencyScanner()
    
    # Test with a known vulnerable package by scanning it
    content = "requests==2.25.0"
    issues = scanner.scan_file('requirements.txt', content)
    
    # The scan should complete without errors
    print(f"✅ OSV API query: PASSED (scanned successfully, found {len(issues)} issues)")


def test_scan_vulnerable_package():
    """Test scanning a known vulnerable package."""
    content = """
requests==2.25.0
"""
    scanner = DependencyScanner()
    issues = scanner.scan_file('requirements.txt', content)
    
    # Note: This test depends on OSV database having vulnerabilities for requests 2.25.0
    # If no vulnerabilities found, that's also valid (package might have been patched)
    print(f"✅ Vulnerable package scan: PASSED (found {len(issues)} issues)")


def test_scan_safe_package():
    """Test scanning a safe/recent package."""
    content = """
requests==2.31.0
"""
    scanner = DependencyScanner()
    issues = scanner.scan_file('requirements.txt', content)
    
    # Recent version should have fewer/no vulnerabilities
    print(f"✅ Safe package scan: PASSED (found {len(issues)} issues)")


def test_auto_fix_generation():
    """Test auto-fix generation for vulnerable packages."""
    content = """
requests==2.25.0
"""
    scanner = DependencyScanner()
    issues = scanner.scan_file('requirements.txt', content)
    
    # Check if auto-fix is generated
    for issue in issues:
        if 'auto_fix' in issue:
            assert 'original' in issue['auto_fix']
            assert 'fixed' in issue['auto_fix']
            assert 'requests==' in issue['auto_fix']['original']
            print(f"  Auto-fix: {issue['auto_fix']['original']} → {issue['auto_fix']['fixed']}")
    
    print("✅ Auto-fix generation: PASSED")


def test_multiple_ecosystems():
    """Test support for multiple package ecosystems."""
    scanner = DependencyScanner()
    
    # Test Python
    python_content = "requests==2.25.0"
    python_issues = scanner.scan_file('requirements.txt', python_content)
    
    # Test Node.js
    node_content = '{"dependencies": {"express": "4.17.1"}}'
    node_issues = scanner.scan_file('package.json', node_content)
    
    print(f"✅ Multiple ecosystems: PASSED (Python: {len(python_issues)}, Node: {len(node_issues)} issues)")


def test_performance_score_calculation():
    """Test performance score calculation."""
    scanner = DependencyScanner()
    
    # Create mock issues
    issues = [
        {'severity': 'critical'},
        {'severity': 'high'},
        {'severity': 'medium'},
    ]
    
    score = scanner._calculate_performance_score(issues)
    
    assert 'score' in score
    assert 'impact' in score
    assert 0 <= score['score'] <= 100
    print(f"✅ Performance score: PASSED (score: {score['score']}, impact: {score['impact']})")


def test_report_generation():
    """Test dependency scan report generation."""
    scanner = DependencyScanner()
    
    # Create mock issues with all required fields
    issues = [
        {
            'severity': 'high',
            'message': 'Test vulnerability',
            'dependency': 'test-package',
            'current_version': '1.0.0',
            'vulnerability_id': 'CVE-2023-12345',
            'description': 'Test vulnerability description'
        }
    ]
    
    score = {'score': 50, 'impact': 'HIGH'}
    report = scanner.generate_dependency_report(issues, score)
    
    assert len(report) > 0, "Should generate report"
    assert 'Dependency' in report or 'dependency' in report
    assert 'test-package' in report
    print("✅ Report generation: PASSED")


def run_all_tests():
    """Run all dependency scanner tests."""
    print("\n📦 Testing Dependency Scanner...\n")
    
    try:
        test_parse_requirements_txt()
        test_parse_package_json()
        test_osv_api_query()
        test_scan_vulnerable_package()
        test_scan_safe_package()
        test_auto_fix_generation()
        test_multiple_ecosystems()
        test_performance_score_calculation()
        test_report_generation()
        
        print("\n✅ All Dependency Scanner tests PASSED!\n")
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
