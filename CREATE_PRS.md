# How to Create Pull Requests on GitHub

All branches are already pushed to GitHub. You need to create Pull Requests manually. Here are the steps:

## Option 1: Using GitHub Web Interface

### For each branch, follow these steps:

1. Go to: https://github.com/TarikYil/DropSpot
2. Click on "Pull requests" tab
3. Click "New pull request"
4. Select base branch: `main`
5. Select compare branch: `feature/[service-name]`
6. Use the PR description from `PR_TEMPLATES.md`

### Branch List:
- `feature/auth-service` → `main`
- `feature/backend-service` → `main`
- `feature/frontend` → `main`
- `feature/ai-service` → `main`
- `feature/test-service` → `main`
- `feature/database-migrations` → `main`

## Option 2: Using GitHub CLI (if installed)

Run these commands:

```bash
# Auth Service PR
gh pr create --base main --head feature/auth-service --title "feat: Add Authentication Service with JWT and Role Management" --body-file PR_TEMPLATES.md

# Backend Service PR
gh pr create --base main --head feature/backend-service --title "feat: Add Backend Service with Drop Management, Waitlist, and Claim System" --body-file PR_TEMPLATES.md

# Frontend PR
gh pr create --base main --head feature/frontend --title "feat: Add React Frontend Application with Modern UI" --body-file PR_TEMPLATES.md

# AI Service PR
gh pr create --base main --head feature/ai-service --title "feat: Add AI Service with Gemini-based RAG Chatbot" --body-file PR_TEMPLATES.md

# Test Service PR
gh pr create --base main --head feature/test-service --title "feat: Add Comprehensive Test Suite with Unit and Integration Tests" --body-file PR_TEMPLATES.md

# Database Migrations PR
gh pr create --base main --head feature/database-migrations --title "feat: Add Database Migration System with Alembic" --body-file PR_TEMPLATES.md
```

## Quick Links to Create PRs

- Auth Service: https://github.com/TarikYil/DropSpot/compare/main...feature/auth-service
- Backend Service: https://github.com/TarikYil/DropSpot/compare/main...feature/backend-service
- Frontend: https://github.com/TarikYil/DropSpot/compare/main...feature/frontend
- AI Service: https://github.com/TarikYil/DropSpot/compare/main...feature/ai-service
- Test Service: https://github.com/TarikYil/DropSpot/compare/main...feature/test-service
- Database Migrations: https://github.com/TarikYil/DropSpot/compare/main...feature/database-migrations

Click on any link above to directly create a PR for that branch.

