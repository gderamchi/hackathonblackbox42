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

## 🚀 Quick Start

### 1. Setup in Your Repository

1. **Copy the workflow file** to your repository:
   ```bash
   mkdir -p .github/workflows
   cp .github/workflows/pr-review.yml .github/workflows/
   ```

2. **Add Blackbox API Key** as a repository secret:
   - Go to your repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `BLACKBOX_API_KEY`
   - Value: Your Blackbox API key

3. **Add GitHub Token** (automatically available as `GITHUB_TOKEN`)

### 2. Configuration (Optional)

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

### 3. Usage

Once set up, the bot automatically:
- ✅ Triggers on PR open/update events
- ✅ Analyzes all changed files
- ✅ Posts review comments
- ✅ Generates PR summary

## 📋 How It Works

1. **PR Event Trigger** - GitHub Actions detects PR creation/update
2. **Fetch Changes** - Retrieves diff and changed files
3. **Blackbox Analysis** - Sends code to Blackbox API for AI-powered review
4. **Multi-Layer Analysis**:
   - Bug pattern detection
   - Security vulnerability scanning
   - Code quality assessment
   - Documentation suggestions
5. **Post Comments** - Creates inline comments and summary
6. **Update Status** - Reports analysis completion

## 🔧 Advanced Configuration

### Custom Rules

Add custom detection rules in `config/rules.json`:

```json
{
  "bug_patterns": [
    {
      "pattern": "eval\\(",
      "message": "Avoid using eval() - security risk",
      "severity": "high"
    }
  ],
  "security_patterns": [
    {
      "pattern": "password\\s*=\\s*['\"]",
      "message": "Hardcoded password detected",
      "severity": "critical"
    }
  ]
}
```

### Environment Variables

- `BLACKBOX_API_KEY` - Your Blackbox API key (required)
- `GITHUB_TOKEN` - GitHub token for API access (auto-provided)
- `MIN_SEVERITY` - Minimum severity to report (info/low/medium/high/critical)
- `MAX_COMMENTS` - Maximum comments per PR (default: 50)

## 🏗️ Architecture

```
┌─────────────────┐
│   GitHub PR     │
│   Event         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│ Workflow        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PR Review Bot  │
│  (Python)       │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│Blackbox│ │ GitHub   │
│  API   │ │   API    │
└────────┘ └──────────┘
```

## 📊 Example Output

### Inline Comment Example
```
🐛 Bug Detected (Medium Severity)

Potential null pointer exception. The variable `user` may be null here.

Suggestion: Add null check before accessing properties:
if user is not None:
    print(user.name)

📚 Related Documentation: [Python None Handling](https://docs.python.org/3/library/stdtypes.html#the-null-object)
```

### PR Summary Example
```
## 🤖 Blackbox PR Review Summary

**Overall Assessment**: ⚠️ Needs Attention

### 📊 Statistics
- Files Changed: 5
- Lines Added: 120
- Lines Removed: 45
- Issues Found: 3

### 🔍 Key Findings
- 🐛 1 potential bug detected
- 🔒 1 security concern
- ℹ️ 1 code quality suggestion

### 📝 Summary
This PR adds user authentication functionality. The implementation is mostly solid, but there are a few concerns that should be addressed before merging.

### ⚠️ Critical Issues
1. Hardcoded API key in `auth.py:23`

### 💡 Recommendations
- Add input validation for user credentials
- Consider using environment variables for secrets
- Add unit tests for authentication flow
```

## 🧪 Testing

Run tests locally:
```bash
pip install -r requirements.txt
pytest tests/
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- [Blackbox AI](https://www.blackbox.ai/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Issue Tracker](https://github.com/yourusername/pr-review-bot/issues)

## 💬 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review example configurations

---

Made with ❤️ using Blackbox AI
