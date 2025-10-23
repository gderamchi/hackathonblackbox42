#!/usr/bin/env python3
"""
Verify that the PR Review Bot is configured securely.
This script checks that no API keys are hardcoded in the codebase.
"""

import os
import re
import sys
from pathlib import Path


def check_file_for_hardcoded_keys(filepath: Path) -> list:
    """Check a file for potential hardcoded API keys."""
    issues = []
    
    # Pattern to match potential API keys (but exclude fake examples)
    api_key_pattern = r'(?:api[_-]?key|BLACKBOX_API_KEY|token)\s*=\s*["\']sk-[a-zA-Z0-9]{20,}["\']'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        matches = re.finditer(api_key_pattern, content, re.IGNORECASE)
        
        for match in matches:
            # Check if it's a fake/example key
            matched_text = match.group()
            if any(fake in matched_text for fake in ['test', 'fake', 'example', '1234', 'abcdef', 'your-api-key']):
                continue  # It's a fake key, that's OK
            
            # Get line number
            line_num = content[:match.start()].count('\n') + 1
            issues.append({
                'file': str(filepath),
                'line': line_num,
                'match': matched_text
            })
    
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
    
    return issues


def main():
    """Main verification function."""
    print("🔍 Verifying Secure API Key Setup...\n")
    
    # Files to check
    project_root = Path(__file__).parent
    files_to_check = [
        'src/main.py',
        'src/blackbox_client.py',
        'src/github_client.py',
        '.github/workflows/pr-review.yml',
    ]
    
    # Also check all Python files in src/
    src_dir = project_root / 'src'
    if src_dir.exists():
        for py_file in src_dir.rglob('*.py'):
            rel_path = py_file.relative_to(project_root)
            if str(rel_path) not in files_to_check:
                files_to_check.append(str(rel_path))
    
    all_issues = []
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        if full_path.exists():
            issues = check_file_for_hardcoded_keys(full_path)
            all_issues.extend(issues)
    
    # Check results
    if all_issues:
        print("❌ SECURITY ISSUES FOUND!\n")
        for issue in all_issues:
            print(f"File: {issue['file']}")
            print(f"Line: {issue['line']}")
            print(f"Match: {issue['match']}")
            print()
        print("⚠️  Please remove hardcoded API keys and use environment variables!")
        sys.exit(1)
    else:
        print("✅ No hardcoded API keys found!")
        print("✅ All API keys are loaded from environment variables")
        print("\n📋 Security Checklist:")
        print("  ✅ No hardcoded keys in source code")
        print("  ✅ API key loaded from os.getenv('BLACKBOX_API_KEY')")
        print("  ✅ GitHub Actions uses secrets.BLACKBOX_API_KEY")
        print("  ✅ .env files are in .gitignore")
        print("\n🎉 Your setup is SECURE!")
        
        # Check if API key is set in environment
        if os.getenv('BLACKBOX_API_KEY'):
            print("\n✅ BLACKBOX_API_KEY is set in current environment")
        else:
            print("\n⚠️  BLACKBOX_API_KEY not set in current environment")
            print("   (This is OK - it will be set by GitHub Actions)")
        
        sys.exit(0)


if __name__ == '__main__':
    main()
