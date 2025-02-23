# Daily Development Workflow

## 1. Start Your Day
```bash
# Update your code
git pull origin main

# Activate environment
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Verify setup
python -m pytest -v
```

## 2. Start New Feature
1. Create CR and branch:
   ```bash
   ./scripts/cr.sh create "Feature title" "Description" "feature"
   ```
   This creates:
   - GitHub issue
   - Feature branch
   - CR document

2. Update documentation:
   - Add to feature's OVERVIEW.md
   - Create design docs if needed
   - Start feature journal

## 3. Development Cycle
1. Write tests first (TDD)
2. Implement feature
3. Update documentation
4. Commit changes:
   ```bash
   git commit -m "type(scope): message (#issue)"
   ```

## 4. Complete Feature
1. Final testing:
   ```bash
   # Backend
   python -m pytest -v

   # Frontend
   npm test
   ```

2. Code quality:
   ```bash
   # Backend
   flake8 .
   black .
   mypy .

   # Frontend
   npm run lint
   npm run format
   ```

3. Update CR status:
   ```bash
   ./scripts/cr.sh update <issue-number> "in-review" "Ready for review"
   ```

4. Create PR:
   - Title: Feature description (#issue)
   - Description: Implementation details
   - Link CR document

## 5. After Review
1. Address feedback
2. Update tests if needed
3. Finalize CR:
   ```bash
   ./scripts/cr.sh finalize <issue-number> "CR-YYYY.MM-N"
   ```

See `detailed/` directory for comprehensive documentation.
