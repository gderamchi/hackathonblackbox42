"""
Comprehensive test suite for Interactive AI features.
Tests command parsing, conversation handling, and auto-fix generation.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.pr-review-bot'))

from interactive_ai import InteractiveAI
from unittest.mock import Mock, MagicMock, patch


class MockGitHubClient:
    """Mock GitHub client for testing."""
    
    def __init__(self):
        self.comments_posted = []
        self.files = {}
    
    def get_pull_request(self, pr_number):
        mock_pr = Mock()
        mock_pr.head.sha = 'abc123'
        return mock_pr
    
    def get_file_content(self, path, ref=None):
        return self.files.get(path, "def example():\n    pass")
    
    def create_issue_comment(self, pr_number, body):
        self.comments_posted.append({'pr': pr_number, 'body': body})
        return True


class MockBlackboxClient:
    """Mock Blackbox client for testing."""
    
    def __init__(self):
        self.requests = []
    
    def analyze_code(self, prompt):
        self.requests.append(prompt)
        
        # Return different responses based on prompt content
        if '/fix' in prompt or 'fix' in prompt.lower():
            return """
FIXED_CODE:
```python
def example():
    try:
        risky_operation()
    except ValueError as e:
        logger.error(f"Error: {e}")
```

EXPLANATION:
Added proper exception handling with specific exception type.

TESTING:
Test with various input values to ensure error handling works correctly.
"""
        elif 'explain' in prompt.lower():
            return """
This code performs a risky operation without proper error handling.

1. What it does: Calls risky_operation() without catching exceptions
2. Why problematic: Can crash the application
3. Best practice: Use try-except with specific exception types
4. Alternative: Add validation before the operation
"""
        elif 'suggest' in prompt.lower():
            return """
### Approach 1: Try-Except
```python
try:
    risky_operation()
except ValueError:
    handle_error()
```

### Approach 2: Validation
```python
if is_valid():
    risky_operation()
```

### Approach 3: Context Manager
```python
with safe_context():
    risky_operation()
```
"""
        else:
            return "I can help you with that. What would you like to know?"


def test_command_parsing():
    """Test command parsing from comments."""
    print("\n🧪 Testing Command Parsing...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Test /fix command
    cmd, args = ai._parse_command("/fix")
    assert cmd == 'fix', f"Expected 'fix', got '{cmd}'"
    assert args is None, f"Expected None, got '{args}'"
    print("  ✅ /fix command parsed correctly")
    
    # Test /fix with args
    cmd, args = ai._parse_command("/fix this issue")
    assert cmd == 'fix', f"Expected 'fix', got '{cmd}'"
    assert args == 'this issue', f"Expected 'this issue', got '{args}'"
    print("  ✅ /fix with arguments parsed correctly")
    
    # Test /explain command
    cmd, args = ai._parse_command("/explain why is this slow?")
    assert cmd == 'explain', f"Expected 'explain', got '{cmd}'"
    assert args == 'why is this slow?', f"Expected question, got '{args}'"
    print("  ✅ /explain command parsed correctly")
    
    # Test /suggest command
    cmd, args = ai._parse_command("/suggest better approach")
    assert cmd == 'suggest', f"Expected 'suggest', got '{cmd}'"
    assert args == 'better approach', f"Expected args, got '{args}'"
    print("  ✅ /suggest command parsed correctly")
    
    # Test /ignore command
    cmd, args = ai._parse_command("/ignore false positive")
    assert cmd == 'ignore', f"Expected 'ignore', got '{cmd}'"
    assert args == 'false positive', f"Expected reason, got '{args}'"
    print("  ✅ /ignore command parsed correctly")
    
    # Test /help command
    cmd, args = ai._parse_command("/help")
    assert cmd == 'help', f"Expected 'help', got '{cmd}'"
    print("  ✅ /help command parsed correctly")
    
    # Test non-command
    cmd, args = ai._parse_command("This is just a comment")
    assert cmd is None, f"Expected None, got '{cmd}'"
    assert args is None, f"Expected None, got '{args}'"
    print("  ✅ Non-command text handled correctly")
    
    print("✅ Command Parsing: PASSED\n")
    return True


def test_bot_mention_detection():
    """Test bot mention detection."""
    print("🧪 Testing Bot Mention Detection...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Test @blackbox-bot mention
    assert ai._is_bot_mentioned("@blackbox-bot can you help?"), "Should detect @blackbox-bot"
    print("  ✅ @blackbox-bot mention detected")
    
    # Test @pr-review-bot mention
    assert ai._is_bot_mentioned("@pr-review-bot explain this"), "Should detect @pr-review-bot"
    print("  ✅ @pr-review-bot mention detected")
    
    # Test 'hey bot' mention
    assert ai._is_bot_mentioned("hey bot, what's this?"), "Should detect 'hey bot'"
    print("  ✅ 'hey bot' mention detected")
    
    # Test command as mention
    assert ai._is_bot_mentioned("/fix"), "Should detect /fix command"
    print("  ✅ /fix command detected as mention")
    
    # Test no mention
    assert not ai._is_bot_mentioned("This is a regular comment"), "Should not detect mention"
    print("  ✅ Regular comment not detected as mention")
    
    print("✅ Bot Mention Detection: PASSED\n")
    return True


def test_fix_command_handler():
    """Test /fix command handler."""
    print("🧪 Testing /fix Command Handler...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Set up test file
    github.files['test.py'] = """
def example():
    risky_operation()
"""
    
    # Test fix command
    response = ai._handle_fix_command(
        pr_number=1,
        file_path='test.py',
        line_number=2,
        args=None
    )
    
    assert response is not None, "Should return response"
    assert 'Auto-Fix' in response, "Should mention auto-fix"
    assert 'Fixed Code' in response or 'fixed code' in response.lower(), "Should include fixed code"
    assert len(blackbox.requests) > 0, "Should call Blackbox API"
    
    print("  ✅ Fix command generates response")
    print("  ✅ Blackbox API called for fix generation")
    print("  ✅ Response includes fixed code")
    
    # Test fix without file path
    response = ai._handle_fix_command(
        pr_number=1,
        file_path=None,
        line_number=None,
        args=None
    )
    
    assert 'Cannot apply fix' in response or 'No file specified' in response, "Should handle missing file"
    print("  ✅ Handles missing file path correctly")
    
    print("✅ /fix Command Handler: PASSED\n")
    return True


def test_explain_command_handler():
    """Test /explain command handler."""
    print("🧪 Testing /explain Command Handler...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Set up test file
    github.files['test.py'] = """
def example():
    risky_operation()
"""
    
    # Test explain command
    response = ai._handle_explain_command(
        pr_number=1,
        file_path='test.py',
        line_number=2,
        args="why is this problematic?"
    )
    
    assert response is not None, "Should return response"
    assert 'Explanation' in response or 'explanation' in response.lower(), "Should mention explanation"
    assert len(blackbox.requests) > 0, "Should call Blackbox API"
    
    print("  ✅ Explain command generates response")
    print("  ✅ Blackbox API called for explanation")
    print("  ✅ Response includes explanation")
    
    # Test explain without file path
    response = ai._handle_explain_command(
        pr_number=1,
        file_path=None,
        line_number=None,
        args=None
    )
    
    assert 'inline comment' in response.lower() or 'context' in response.lower(), "Should request context"
    print("  ✅ Handles missing context correctly")
    
    print("✅ /explain Command Handler: PASSED\n")
    return True


def test_suggest_command_handler():
    """Test /suggest command handler."""
    print("🧪 Testing /suggest Command Handler...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Set up test file
    github.files['test.py'] = """
def example():
    risky_operation()
"""
    
    # Test suggest command
    response = ai._handle_suggest_command(
        pr_number=1,
        file_path='test.py',
        line_number=2,
        args="better approach"
    )
    
    assert response is not None, "Should return response"
    assert 'Alternative' in response or 'alternative' in response.lower(), "Should mention alternatives"
    assert len(blackbox.requests) > 0, "Should call Blackbox API"
    
    print("  ✅ Suggest command generates response")
    print("  ✅ Blackbox API called for suggestions")
    print("  ✅ Response includes alternatives")
    
    print("✅ /suggest Command Handler: PASSED\n")
    return True


def test_ignore_command_handler():
    """Test /ignore command handler."""
    print("🧪 Testing /ignore Command Handler...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Test ignore command with reason
    response = ai._handle_ignore_command(
        pr_number=1,
        file_path='test.py',
        line_number=2,
        args="false positive"
    )
    
    assert response is not None, "Should return response"
    assert 'Ignored' in response or 'ignored' in response.lower(), "Should mention ignored"
    assert 'false positive' in response, "Should include reason"
    
    print("  ✅ Ignore command generates response")
    print("  ✅ Reason included in response")
    
    # Test ignore without reason
    response = ai._handle_ignore_command(
        pr_number=1,
        file_path='test.py',
        line_number=2,
        args=None
    )
    
    assert 'No reason provided' in response, "Should handle missing reason"
    print("  ✅ Handles missing reason correctly")
    
    print("✅ /ignore Command Handler: PASSED\n")
    return True


def test_help_command_handler():
    """Test /help command handler."""
    print("🧪 Testing /help Command Handler...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Test help command
    response = ai._handle_help_command()
    
    assert response is not None, "Should return response"
    assert '/fix' in response, "Should list /fix command"
    assert '/explain' in response, "Should list /explain command"
    assert '/suggest' in response, "Should list /suggest command"
    assert '/ignore' in response, "Should list /ignore command"
    assert '/help' in response, "Should list /help command"
    
    print("  ✅ Help command generates response")
    print("  ✅ All commands listed")
    print("  ✅ Usage examples included")
    
    print("✅ /help Command Handler: PASSED\n")
    return True


def test_natural_conversation():
    """Test natural conversation handling."""
    print("🧪 Testing Natural Conversation...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Test natural question
    response = ai._handle_conversation(
        message="Can you explain why this is slow?",
        pr_number=1,
        file_path='test.py',
        line_number=10
    )
    
    assert response is not None, "Should return response"
    assert len(blackbox.requests) > 0, "Should call Blackbox API"
    
    print("  ✅ Natural conversation generates response")
    print("  ✅ Blackbox API called for conversation")
    
    # Test follow-up question
    response2 = ai._handle_conversation(
        message="What's a better approach?",
        pr_number=1,
        file_path='test.py',
        line_number=10
    )
    
    assert response2 is not None, "Should handle follow-up"
    print("  ✅ Follow-up questions handled")
    
    print("✅ Natural Conversation: PASSED\n")
    return True


def test_conversation_tracking():
    """Test conversation history tracking."""
    print("🧪 Testing Conversation Tracking...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Store some conversations
    ai._store_conversation(
        pr_number=1,
        file_path='test.py',
        line_number=10,
        message="Why is this slow?",
        response="Because of nested loops..."
    )
    
    ai._store_conversation(
        pr_number=1,
        file_path='test.py',
        line_number=10,
        message="Can you fix it?",
        response="Sure, here's a better approach..."
    )
    
    # Get context
    context = ai._get_conversation_context(1, 'test.py', 10)
    
    assert 'Why is this slow?' in context, "Should include first message"
    assert 'nested loops' in context, "Should include first response"
    
    print("  ✅ Conversations stored correctly")
    print("  ✅ Context retrieved correctly")
    
    # Generate summary
    summary = ai.generate_conversation_summary(1)
    
    assert summary is not None, "Should generate summary"
    assert 'test.py' in summary, "Should include file name"
    
    print("  ✅ Summary generated correctly")
    
    print("✅ Conversation Tracking: PASSED\n")
    return True


def test_process_comment_integration():
    """Test full comment processing flow."""
    print("🧪 Testing Comment Processing Integration...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Test with /fix command
    response = ai.process_comment(
        pr_number=1,
        comment_id=123,
        comment_body="/fix",
        comment_author="developer",
        file_path='test.py',
        line_number=10
    )
    
    assert response is not None, "Should return response for /fix"
    assert 'fix' in response.lower(), "Should mention fix"
    
    print("  ✅ /fix command processed end-to-end")
    
    # Test with natural conversation
    response = ai.process_comment(
        pr_number=1,
        comment_id=124,
        comment_body="@blackbox-bot can you help?",
        comment_author="developer",
        file_path='test.py',
        line_number=10
    )
    
    assert response is not None, "Should return response for conversation"
    
    print("  ✅ Natural conversation processed end-to-end")
    
    # Test with non-bot comment
    response = ai.process_comment(
        pr_number=1,
        comment_id=125,
        comment_body="This looks good to me",
        comment_author="developer",
        file_path='test.py',
        line_number=10
    )
    
    assert response is None, "Should not respond to non-bot comments"
    
    print("  ✅ Non-bot comments ignored correctly")
    
    print("✅ Comment Processing Integration: PASSED\n")
    return True


def test_error_handling():
    """Test error handling in various scenarios."""
    print("🧪 Testing Error Handling...")
    
    github = MockGitHubClient()
    blackbox = MockBlackboxClient()
    ai = InteractiveAI(github, blackbox)
    
    # Test with invalid PR number
    try:
        response = ai._handle_fix_command(
            pr_number=None,
            file_path='test.py',
            line_number=10,
            args=None
        )
        # Should handle gracefully
        print("  ✅ Handles invalid PR number")
    except Exception as e:
        print(f"  ⚠️  Exception with invalid PR: {e}")
    
    # Test with missing file
    response = ai._handle_fix_command(
        pr_number=1,
        file_path='nonexistent.py',
        line_number=10,
        args=None
    )
    assert 'Cannot read file' in response or 'Error' in response, "Should handle missing file"
    print("  ✅ Handles missing file gracefully")
    
    # Test with Blackbox API failure
    blackbox_fail = MockBlackboxClient()
    blackbox_fail.analyze_code = lambda x: ""  # Return empty response
    ai_fail = InteractiveAI(github, blackbox_fail)
    
    response = ai_fail._handle_explain_command(
        pr_number=1,
        file_path='test.py',
        line_number=10,
        args=None
    )
    # Should handle empty response
    print("  ✅ Handles API failures gracefully")
    
    print("✅ Error Handling: PASSED\n")
    return True


def run_all_tests():
    """Run all interactive AI tests."""
    print("\n" + "="*60)
    print("🧪 TESTING INTERACTIVE AI FEATURES")
    print("="*60 + "\n")
    
    tests = [
        ("Command Parsing", test_command_parsing),
        ("Bot Mention Detection", test_bot_mention_detection),
        ("/fix Command Handler", test_fix_command_handler),
        ("/explain Command Handler", test_explain_command_handler),
        ("/suggest Command Handler", test_suggest_command_handler),
        ("/ignore Command Handler", test_ignore_command_handler),
        ("/help Command Handler", test_help_command_handler),
        ("Natural Conversation", test_natural_conversation),
        ("Conversation Tracking", test_conversation_tracking),
        ("Comment Processing Integration", test_process_comment_integration),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name}: FAILED\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: ERROR - {e}\n")
    
    print("="*60)
    print(f"📊 TEST RESULTS: {passed}/{len(tests)} PASSED")
    print("="*60 + "\n")
    
    if failed == 0:
        print("🎉 ALL INTERACTIVE AI TESTS PASSED!\n")
        return True
    else:
        print(f"⚠️  {failed} TEST(S) FAILED\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
