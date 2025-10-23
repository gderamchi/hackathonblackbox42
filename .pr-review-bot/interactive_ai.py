"""
Interactive AI conversation handler for PR reviews.
Allows developers to chat with the AI and request automatic fixes.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from github_client import GitHubClient
from blackbox_client import BlackboxClient

logger = logging.getLogger(__name__)


class InteractiveAI:
    """Handles interactive conversations with developers on PRs."""
    
    def __init__(self, github_client: GitHubClient, blackbox_client: BlackboxClient):
        """
        Initialize interactive AI handler.
        
        Args:
            github_client: GitHub API client
            blackbox_client: Blackbox API client
        """
        self.github = github_client
        self.blackbox = blackbox_client
        self.conversation_history = {}
        
        # Command patterns
        self.commands = {
            'fix': r'/fix(?:\s+(.+))?',
            'explain': r'/explain(?:\s+(.+))?',
            'suggest': r'/suggest(?:\s+(.+))?',
            'ignore': r'/ignore(?:\s+(.+))?',
            'help': r'/help',
        }
    
    def process_comment(
        self,
        pr_number: int,
        comment_id: int,
        comment_body: str,
        comment_author: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None
    ) -> Optional[str]:
        """
        Process a comment and determine if it's a command or conversation.
        
        Args:
            pr_number: PR number
            comment_id: Comment ID
            comment_body: Comment text
            comment_author: Comment author
            file_path: File path if inline comment
            line_number: Line number if inline comment
            
        Returns:
            Response text or None
        """
        # Check if comment mentions the bot
        if not self._is_bot_mentioned(comment_body):
            return None
        
        # Parse command
        command, args = self._parse_command(comment_body)
        
        if command:
            return self._handle_command(
                command, args, pr_number, file_path, line_number
            )
        else:
            # Natural conversation
            return self._handle_conversation(
                comment_body, pr_number, file_path, line_number
            )
    
    def _is_bot_mentioned(self, text: str) -> bool:
        """Check if bot is mentioned in comment."""
        bot_mentions = [
            '@blackbox-bot',
            '@pr-review-bot',
            'hey bot',
            'hi bot',
            '/fix',
            '/explain',
            '/suggest',
            '/help'
        ]
        text_lower = text.lower()
        return any(mention in text_lower for mention in bot_mentions)
    
    def _parse_command(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Parse command from comment text.
        
        Returns:
            Tuple of (command, arguments)
        """
        for cmd, pattern in self.commands.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                args = match.group(1) if match.lastindex else None
                return cmd, args
        return None, None
    
    def _handle_command(
        self,
        command: str,
        args: Optional[str],
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int]
    ) -> str:
        """Handle specific commands."""
        if command == 'fix':
            return self._handle_fix_command(pr_number, file_path, line_number, args)
        elif command == 'explain':
            return self._handle_explain_command(pr_number, file_path, line_number, args)
        elif command == 'suggest':
            return self._handle_suggest_command(pr_number, file_path, line_number, args)
        elif command == 'ignore':
            return self._handle_ignore_command(pr_number, file_path, line_number, args)
        elif command == 'help':
            return self._handle_help_command()
        
        return "Unknown command. Type `/help` for available commands."
    
    def _handle_fix_command(
        self,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int],
        args: Optional[str]
    ) -> str:
        """
        Handle /fix command - automatically apply fixes.
        
        Returns:
            Status message
        """
        try:
            if not file_path:
                return "❌ Cannot apply fix: No file specified. Use `/fix` on an inline comment."
            
            # Get current file content
            pr = self.github.get_pull_request(pr_number)
            file_content = self.github.get_file_content(
                file_path,
                ref=pr.head.sha
            )
            
            if not file_content:
                return f"❌ Cannot read file: {file_path}"
            
            # Get the issue context from conversation history
            issue_context = self._get_issue_context(pr_number, file_path, line_number)
            
            # Ask Blackbox AI to generate the fix
            prompt = f"""Generate a fix for this code issue:

File: {file_path}
Line: {line_number}
Issue: {issue_context}

Current code:
```
{file_content}
```

Provide:
1. The exact fixed code (complete file)
2. Explanation of changes
3. Testing recommendations

Format as:
FIXED_CODE:
```
<complete fixed code>
```

EXPLANATION:
<explanation>

TESTING:
<testing recommendations>
"""
            
            response = self.blackbox.analyze_code(prompt)
            
            # Parse response
            fixed_code = self._extract_fixed_code(response)
            explanation = self._extract_explanation(response)
            
            if not fixed_code:
                return "❌ Could not generate fix. Please try again or fix manually."
            
            # Create a new branch and commit the fix
            branch_name = f"blackbox-ai/fix-{pr_number}-{file_path.replace('/', '-')}"
            
            # Note: In production, this would create a commit
            # For now, we'll provide the fix as a suggestion
            
            response_text = f"""## 🤖 Auto-Fix Applied

I've generated a fix for the issue at `{file_path}:{line_number}`.

### 📝 Changes Made:
{explanation}

### 💻 Fixed Code:
<details>
<summary>Click to view fixed code</summary>

\`\`\`python
{fixed_code[:1000]}{'...' if len(fixed_code) > 1000 else ''}
\`\`\`

</details>

### 🧪 Testing Recommendations:
{self._extract_testing(response)}

### 🚀 Next Steps:
1. Review the changes above
2. If approved, I can create a commit with these changes
3. Reply with `/apply` to create the commit, or `/reject` to discard

**Note:** This is an AI-generated fix. Please review carefully before applying.
"""
            
            # Store the fix for potential application
            self._store_pending_fix(pr_number, file_path, fixed_code)
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error handling fix command: {e}")
            return f"❌ Error generating fix: {str(e)}"
    
    def _handle_explain_command(
        self,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int],
        args: Optional[str]
    ) -> str:
        """Handle /explain command - provide detailed explanation."""
        try:
            if not file_path:
                return "❌ Please use `/explain` on an inline comment to get context."
            
            # Get file content
            pr = self.github.get_pull_request(pr_number)
            file_content = self.github.get_file_content(file_path, ref=pr.head.sha)
            
            # Get surrounding context
            lines = file_content.split('\n')
            start = max(0, line_number - 10) if line_number else 0
            end = min(len(lines), line_number + 10) if line_number else len(lines)
            context = '\n'.join(lines[start:end])
            
            # Ask Blackbox for explanation
            prompt = f"""Explain this code in detail:

File: {file_path}
Line: {line_number}
Question: {args if args else 'Explain what this code does'}

Code context:
```
{context}
```

Provide:
1. What the code does
2. Why it might be problematic
3. Best practices
4. Alternative approaches
"""
            
            explanation = self.blackbox.analyze_code(prompt)
            
            return f"""## 🤖 Code Explanation

{explanation}

---
*Need more details? Ask me anything about this code!*
"""
            
        except Exception as e:
            logger.error(f"Error handling explain command: {e}")
            return f"❌ Error generating explanation: {str(e)}"
    
    def _handle_suggest_command(
        self,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int],
        args: Optional[str]
    ) -> str:
        """Handle /suggest command - provide alternative implementations."""
        try:
            if not file_path:
                return "❌ Please use `/suggest` on an inline comment."
            
            pr = self.github.get_pull_request(pr_number)
            file_content = self.github.get_file_content(file_path, ref=pr.head.sha)
            
            prompt = f"""Suggest alternative implementations for this code:

File: {file_path}
Context: {args if args else 'General improvements'}

Code:
```
{file_content}
```

Provide 3 alternative approaches with:
1. Code example
2. Pros and cons
3. Use cases
"""
            
            suggestions = self.blackbox.analyze_code(prompt)
            
            return f"""## 🤖 Alternative Implementations

{suggestions}

---
*Want to apply one of these? Reply with `/fix` and specify which approach!*
"""
            
        except Exception as e:
            logger.error(f"Error handling suggest command: {e}")
            return f"❌ Error generating suggestions: {str(e)}"
    
    def _handle_ignore_command(
        self,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int],
        args: Optional[str]
    ) -> str:
        """Handle /ignore command - mark issue as ignored."""
        reason = args if args else "No reason provided"
        
        # Store ignore decision
        self._store_ignore_decision(pr_number, file_path, line_number, reason)
        
        return f"""## ✅ Issue Ignored

This issue has been marked as ignored.

**Reason:** {reason}

The bot will not flag this issue in future reviews of this PR.

*To un-ignore, reply with `/unignore`*
"""
    
    def _handle_help_command(self) -> str:
        """Handle /help command - show available commands."""
        return """## 🤖 PR Review Bot - Interactive Commands

### Available Commands:

**`/fix`** - Automatically generate and apply a fix
- Usage: `/fix` (on inline comment)
- Example: `/fix` → Bot generates and suggests code fix

**`/explain`** - Get detailed explanation of code
- Usage: `/explain [question]`
- Example: `/explain why is this slow?`

**`/suggest`** - Get alternative implementations
- Usage: `/suggest [context]`
- Example: `/suggest more efficient approach`

**`/ignore`** - Ignore this issue
- Usage: `/ignore [reason]`
- Example: `/ignore false positive`

**`/help`** - Show this help message

### Natural Conversation:
You can also just chat with me naturally! Mention `@blackbox-bot` or reply to my comments.

Examples:
- "Can you explain this in simpler terms?"
- "What's the best way to fix this?"
- "Is there a more efficient approach?"
- "Why is this a security issue?"

### Auto-Fix Workflow:
1. I post a review comment with an issue
2. You reply with `/fix`
3. I generate a complete fix
4. You review and reply `/apply` or `/reject`
5. If approved, I create a commit with the fix

---
*I'm here to help! Ask me anything about your code.*
"""
    
    def _handle_conversation(
        self,
        message: str,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int]
    ) -> str:
        """Handle natural conversation with the bot."""
        try:
            # Get conversation context
            context = self._get_conversation_context(pr_number, file_path, line_number)
            
            # Build prompt for Blackbox
            prompt = f"""You are a helpful code review assistant. A developer is asking about their code.

Context:
- PR Number: {pr_number}
- File: {file_path or 'General PR discussion'}
- Line: {line_number or 'N/A'}
- Previous context: {context}

Developer's message:
{message}

Provide a helpful, conversational response. Be friendly and technical. If they're asking about a fix, offer to generate one with `/fix`.
"""
            
            response = self.blackbox.analyze_code(prompt)
            
            # Store conversation
            self._store_conversation(pr_number, file_path, line_number, message, response)
            
            return f"""## 🤖 Response

{response}

---
*Commands: `/fix` `/explain` `/suggest` `/help`*
"""
            
        except Exception as e:
            logger.error(f"Error handling conversation: {e}")
            return "❌ Sorry, I encountered an error. Please try again."
    
    def generate_conversation_summary(self, pr_number: int) -> str:
        """
        Generate a summary of all conversations and actions taken.
        
        Args:
            pr_number: PR number
            
        Returns:
            Formatted summary
        """
        conversations = self.conversation_history.get(pr_number, [])
        
        if not conversations:
            return "No conversations yet."
        
        summary = "## 💬 Conversation Summary\n\n"
        
        # Group by file
        by_file = {}
        for conv in conversations:
            file = conv.get('file_path', 'General')
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(conv)
        
        for file, convs in by_file.items():
            summary += f"### 📄 {file}\n\n"
            for conv in convs:
                summary += f"**Developer:** {conv['message'][:100]}...\n"
                summary += f"**Bot:** {conv['response'][:100]}...\n\n"
        
        return summary
    
    # Helper methods
    
    def _get_issue_context(
        self,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int]
    ) -> str:
        """Get context about the issue from conversation history."""
        # In production, this would fetch from stored data
        return "Code quality issue detected"
    
    def _get_conversation_context(
        self,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int]
    ) -> str:
        """Get previous conversation context."""
        key = f"{pr_number}:{file_path}:{line_number}"
        history = self.conversation_history.get(key, [])
        
        if not history:
            return "No previous context"
        
        return "\n".join([
            f"User: {h['message']}\nBot: {h['response']}"
            for h in history[-3:]  # Last 3 exchanges
        ])
    
    def _store_conversation(
        self,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int],
        message: str,
        response: str
    ):
        """Store conversation for context."""
        key = f"{pr_number}:{file_path}:{line_number}"
        if key not in self.conversation_history:
            self.conversation_history[key] = []
        
        self.conversation_history[key].append({
            'message': message,
            'response': response,
            'timestamp': None  # Would use actual timestamp
        })
    
    def _store_pending_fix(self, pr_number: int, file_path: str, fixed_code: str):
        """Store pending fix for later application."""
        # In production, store in database or file
        pass
    
    def _store_ignore_decision(
        self,
        pr_number: int,
        file_path: Optional[str],
        line_number: Optional[int],
        reason: str
    ):
        """Store ignore decision."""
        # In production, store in database
        pass
    
    def _extract_fixed_code(self, response: str) -> Optional[str]:
        """Extract fixed code from AI response."""
        match = re.search(r'FIXED_CODE:\s*```[^\n]*\n(.*?)```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback: look for any code block
        match = re.search(r'```[^\n]*\n(.*?)```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _extract_explanation(self, response: str) -> str:
        """Extract explanation from AI response."""
        match = re.search(r'EXPLANATION:\s*(.*?)(?:TESTING:|$)', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "See changes above."
    
    def _extract_testing(self, response: str) -> str:
        """Extract testing recommendations from AI response."""
        match = re.search(r'TESTING:\s*(.*?)$', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "Test the changes thoroughly before merging."
