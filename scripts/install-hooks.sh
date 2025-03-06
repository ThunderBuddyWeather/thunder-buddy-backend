#!/bin/bash
# Script to install Git hooks

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# Check if we're in the middle of a merge, rebase, etc.
if [ -f .git/MERGE_HEAD ] || [ -f .git/REBASE_HEAD ] || [ -f .git/CHERRY_PICK_HEAD ]; then
    echo "Skipping Swagger generation during merge/rebase/cherry-pick"
    exit 0
fi

# Check if Python files in app/ or run.py have changed
if git diff --cached --name-only | grep -E '(^app/.*\.py$|^run\.py$)'; then
    echo "Python files changed. Generating Swagger documentation..."
    
    # Save current staged changes
    git stash push --keep-index --message "pre-commit-stash" --quiet
    
    # Generate Swagger
    make swagger
    
    # Stage the generated Swagger file if it exists
    if [ -f static/swagger.yaml ]; then
        git add static/swagger.yaml
        echo "Swagger documentation updated and staged."
    else
        echo "Warning: Swagger generation failed or file not found."
    fi
    
    # Restore stashed changes (if any)
    if git stash list | grep -q "pre-commit-stash"; then
        git stash pop --quiet
    fi
fi

exit 0
EOF

# Make the hook executable
chmod +x .git/hooks/pre-commit

echo "Git hooks installed successfully!" 