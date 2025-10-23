# 🤖 Blackbox PR Review Bot

An intelligent Pull Request review bot powered by Blackbox AI that automatically analyzes code changes, detects bugs, identifies security vulnerabilities, and provides actionable feedback.

## ✨ Features

- **🔍 Automated PR Analysis** - Analyzes all code changes in pull requests
- **🐛 Bug Detection** - Identifies common bugs, logic errors, and code smells
- **🔒 Security Scanning** - Detects SQL injection, XSS, hardcoded secrets, and more
- **📚 Documentation Linking** - Suggests relevant documentation for APIs and patterns
- **📝 PR Summarization** - Generates comprehensive summaries of changes
- **💬 Inline Comments** - Posts contextual comments directly on problematic lines
- **⚡ Multi-Language Support** - Works with Python, JavaScript, TypeScript, Java, Go, and more
- **🚀 Scalable** - Handles multiple repositories with configurable rules

## 🚀 Quick Setup (3 Steps)

### Step 1: Create Workflow File
In your new repository, create `.github/workflows/pr-review.yml`:

```yaml
name: PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    uses: gderamchi/hackathonblackbox42/.github/workflows/pr-review.yml@main
    secrets:
      BLACKBOX_API_KEY: ${{ secrets.BLACKBOX_API_KEY }}
```

### Step 2: Add GitHub Secret
1. Go to your repo: `Settings → Secrets → Actions`
2. Click "New repository secret"
3. Name: `BLACKBOX_API_KEY`
4. Value: Your Blackbox API key
5. Click "Add secret"

### Step 3: Enable GitHub Actions
1. Go to: `Settings → Actions → General`
2. Select: "Allow all actions and reusable workflows"
3. Select: "Read and write permissions"
4. Click "Save"

**Done!** Create a PR and the bot will automatically review it.

---

## ⚙️ Optional Configuration

Create a `.pr-review-bot.json` file in your repository root to customize behavior:

```json
{
  "enabled": true,
  "auto_comment": true,
  "severity_threshold": "medium",
  "ignore_patterns": [
    "*.md",
    "*.txt",
    "package-lock.json"
  ],
  "features": {
    "bug_detection": true,
    "security_scan": true,
    "doc_linking": true,
    "summarization": true
  },
  "custom_rules": []
}
```

## 🔍 What Gets Detected

- 🔒 **Security:** SQL injection, XSS, hardcoded secrets, command injection, weak crypto
- 🐛 **Bugs:** Null pointers, division by zero, infinite loops, resource leaks
- 💡 **Quality:** Best practices, code smells, debug code, unused variables

## 📊 Example Output

**Inline Comment:**
```
🐛 Bug Detected (Medium Severity)

Potential null pointer exception. The variable `user` may be null here.

Suggestion: Add null check before accessing properties:
if user is not None:
    print(user.name)
```

**PR Summary:**
```
## 🤖 Blackbox PR Review Summary

**Overall Assessment**: ⚠️ Needs Attention

### 📊 Statistics
- Files Changed: 5
- Issues Found: 3 (1 critical, 1 high, 1 medium)

### ⚠️ Critical Issues
1. Hardcoded API key in `auth.py:23`

### 💡 Recommendations
- Add input validation for user credentials
- Use environment variables for secrets
```

## 📁 Repository Structure

- `.pr-review-bot/` - Bot source code (Python)
- `.github/workflows/pr-review.yml` - Reusable workflow
- `requirements.txt` - Python dependencies
- `config/rules.json` - Custom detection rules

---

Made with ❤️ using Blackbox AI
