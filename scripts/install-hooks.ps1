# PowerShell script to install Git hooks

# Create hooks directory if it doesn't exist
if (-not (Test-Path .git/hooks)) {
    New-Item -ItemType Directory -Path .git/hooks -Force | Out-Null
}

# Create pre-commit hook
$preCommitContent = @'
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
'@

# Write the pre-commit hook
$preCommitContent | Out-File -FilePath .git/hooks/pre-commit -Encoding utf8 -NoNewline

# Make the hook executable (Git for Windows uses Git Bash which respects executable bit)
# This command uses Git's update-index to set the executable bit
git update-index --chmod=+x .git/hooks/pre-commit

Write-Host "Git hooks installed successfully!" -ForegroundColor Green
Write-Host "Note: These hooks require Git Bash to run on Windows." -ForegroundColor Yellow 