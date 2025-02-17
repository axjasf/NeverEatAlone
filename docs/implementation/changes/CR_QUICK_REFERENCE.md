# Change Request Quick Reference

## Key Locations
```
docs/implementation/changes/
├── CHANGE_REQUEST_PROCESS.md   # Full process documentation
├── CHANGE_REQUEST_TEMPLATE.md  # Template for new CRs
├── CR_QUICK_REFERENCE.md      # This quick reference
└── CR-YYYY.MM.DD-N.md         # Individual CR documents
```

## Quick Start Commands
```bash
# 1. Create new CR branch
git checkout -b feature/CR-$(date +%Y.%m.%d)-1-brief-description

# 2. Create CR document
cp docs/implementation/changes/CHANGE_REQUEST_TEMPLATE.md \
   docs/implementation/changes/CR-$(date +%Y.%m.%d)-1.md

# 3. Stage CR document
git add docs/implementation/changes/CR-$(date +%Y.%m.%d)-1.md
git commit -m "docs(cr): create CR-$(date +%Y.%m.%d)-1 for [description]"

# 4. Update docs (in sequence)
for doc in functional architecture interfaces non_functional user_stories data_model; do
  git commit -m "docs($doc): update for CR-$(date +%Y.%m.%d)-1"
done

# 5. Implementation
git commit -m "feat(scope): implement for CR-$(date +%Y.%m.%d)-1"
```

## Documentation Update Sequence
1. Functional Requirements (`docs/brd/modules/contact_management/requirements/functional.md`)
2. Architecture (`docs/brd/modules/contact_management/technical/architecture.md`)
3. Interfaces (`docs/brd/modules/contact_management/technical/interfaces.md`)
4. Non-Functional Requirements (`docs/brd/modules/contact_management/requirements/non_functional.md`)
5. User Stories (`docs/brd/modules/contact_management/requirements/user_stories.md`)
6. Data Model (`docs/brd/modules/contact_management/technical/data_model.md`)
7. Implementation Details:
   - Implementation Plan (`docs/implementation/IMPLEMENTATION_PLAN.md`)
   - Working Notes (`docs/implementation/WORKING_NOTES.md`)

## Version Numbering
- Format: `YYYY.MM.DD-N`
- Example: `2024.02.13-1`
- Increment N for multiple updates in same day

## Commit Message Format
```
docs(scope): update [doc-name] for [CR-number]
feat(scope): implement [feature] for [CR-number]
fix(scope): resolve [issue] for [CR-number]
refactor(scope): improve [component] for [CR-number]
```

## Common CR Types
- Feature Changes: New functionality/enhancements
- Bugfixes: Error corrections/performance fixes
- Refactoring: Code restructuring/improvements
- Documentation: Process/template updates

## Review Checklist
1. Documentation complete and cross-referenced
2. Version numbers consistent
3. All required tests written
4. Implementation follows TDD
5. Commit messages follow format

## Need Help?
1. Full process: See `CHANGE_REQUEST_PROCESS.md`
2. Template: See `CHANGE_REQUEST_TEMPLATE.md`
3. Example: See `INTERACTION_TRACKING_REFACTOR.md`
