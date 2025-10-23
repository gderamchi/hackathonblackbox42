#!/bin/bash

# 🚀 One-Click Deployment Script for PR Review Bot
# This script deploys the bot to any GitHub repository in seconds

set -e

echo "🤖 PR Review Bot - One-Click Deployment"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository. Please run this script from your repository root."
    exit 1
fi

print_success "Git repository detected"

# Get repository information
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
REMOTE_URL=$(git config --get remote.origin.url)

echo ""
print_info "Repository: $REPO_NAME"
print_info "Location: $REPO_ROOT"
echo ""

# Ask for confirmation
read -p "Deploy PR Review Bot to this repository? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Deployment cancelled"
    exit 1
fi

# Create necessary directories
print_info "Creating directory structure..."
mkdir -p "$REPO_ROOT/.github/workflows"
mkdir -p "$REPO_ROOT/src/analyzers"
mkdir -p "$REPO_ROOT/src/utils"
mkdir -p "$REPO_ROOT/config"

# Get the script's directory (where the bot files are)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Copy workflow file
print_info "Copying GitHub Actions workflow..."
if [ -f "$SCRIPT_DIR/.github/workflows/pr-review.yml" ]; then
    cp "$SCRIPT_DIR/.github/workflows/pr-review.yml" "$REPO_ROOT/.github/workflows/"
    print_success "Workflow file copied"
else
    print_error "Workflow file not found. Please ensure you're running from the bot repository."
    exit 1
fi

# Copy source files
print_info "Copying source files..."
cp -r "$SCRIPT_DIR/src/"* "$REPO_ROOT/src/" 2>/dev/null || true
print_success "Source files copied"

# Copy configuration files
print_info "Copying configuration files..."
cp "$SCRIPT_DIR/requirements.txt" "$REPO_ROOT/" 2>/dev/null || true
cp "$SCRIPT_DIR/.pr-review-bot.json" "$REPO_ROOT/" 2>/dev/null || true
cp "$SCRIPT_DIR/config/rules.json" "$REPO_ROOT/config/" 2>/dev/null || true
print_success "Configuration files copied"

# Copy documentation
print_info "Copying documentation..."
cp "$SCRIPT_DIR/SECURE_API_KEY_SETUP.md" "$REPO_ROOT/" 2>/dev/null || true
cp "$SCRIPT_DIR/TEST_THE_BOT.md" "$REPO_ROOT/" 2>/dev/null || true
print_success "Documentation copied"

# Create .env.example if it doesn't exist
if [ ! -f "$REPO_ROOT/.env.example" ]; then
    print_info "Creating .env.example..."
    cat > "$REPO_ROOT/.env.example" << 'EOF'
# Blackbox API Configuration
BLACKBOX_API_KEY=your-api-key-here

# GitHub Token (automatically provided by GitHub Actions)
# GITHUB_TOKEN=your-github-token
EOF
    print_success ".env.example created"
fi

# Update .gitignore
print_info "Updating .gitignore..."
if [ -f "$REPO_ROOT/.gitignore" ]; then
    # Check if .env is already in .gitignore
    if ! grep -q "^\.env$" "$REPO_ROOT/.gitignore"; then
        echo "" >> "$REPO_ROOT/.gitignore"
        echo "# PR Review Bot" >> "$REPO_ROOT/.gitignore"
        echo ".env" >> "$REPO_ROOT/.gitignore"
        echo ".env.local" >> "$REPO_ROOT/.gitignore"
        echo "analysis-results.json" >> "$REPO_ROOT/.gitignore"
        echo "review-summary.md" >> "$REPO_ROOT/.gitignore"
        print_success ".gitignore updated"
    else
        print_info ".env already in .gitignore"
    fi
else
    # Create .gitignore
    cat > "$REPO_ROOT/.gitignore" << 'EOF'
# PR Review Bot
.env
.env.local
analysis-results.json
review-summary.md

# Python
__pycache__/
*.py[cod]
*.so
.Python
EOF
    print_success ".gitignore created"
fi

echo ""
echo "========================================"
print_success "Deployment Complete!"
echo "========================================"
echo ""

# Print next steps
echo "📋 Next Steps:"
echo ""
echo "1. Add GitHub Secret:"
echo "   Go to: https://github.com/YOUR_ORG/$REPO_NAME/settings/secrets/actions"
echo "   Add: BLACKBOX_API_KEY = your-api-key"
echo ""
echo "2. Enable GitHub Actions:"
echo "   Go to: https://github.com/YOUR_ORG/$REPO_NAME/settings/actions"
echo "   Enable: 'Allow all actions' and 'Read and write permissions'"
echo ""
echo "3. Test the bot:"
echo "   Create a test PR and watch the bot in action!"
echo ""
echo "📚 Documentation:"
echo "   - SECURE_API_KEY_SETUP.md - Security setup"
echo "   - TEST_THE_BOT.md - Testing guide"
echo "   - .pr-review-bot.json - Configuration"
echo ""

# Ask if user wants to commit changes
echo ""
read -p "Commit these changes to git? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$REPO_ROOT"
    git add .github/workflows/pr-review.yml
    git add src/
    git add requirements.txt
    git add .pr-review-bot.json
    git add config/
    git add .gitignore
    git add .env.example
    git add *.md 2>/dev/null || true
    
    git commit -m "feat: Add PR Review Bot

- Automated code review on pull requests
- Security vulnerability detection
- Bug pattern detection
- Code quality analysis
- Documentation linking

Powered by Blackbox AI"
    
    print_success "Changes committed!"
    echo ""
    read -p "Push to remote? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push
        print_success "Changes pushed!"
    fi
fi

echo ""
print_success "🎉 All done! Your repository is now equipped with AI-powered PR reviews!"
echo ""
