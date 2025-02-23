# CR Quick Reference

## Commands
```bash
# Create CR
./scripts/cr.sh create "Title" "Description" "feature"

# Update Status
./scripts/cr.sh update <issue-number> "in-progress" "Message"

# Complete CR
./scripts/cr.sh finalize <issue-number> "CR-YYYY.MM-N"
```

## Structure
```
features/N-feature-name/
├── OVERVIEW.md           # Feature summary
├── design/              # Design decisions
└── crs/                # Change requests
    └── CR-YYYY.MM-N.md  # Individual CR
```

## Required Updates
1. Feature OVERVIEW.md
2. Dev journal entries
3. Design documents
4. Test coverage

See `PROCESS.md` for detailed guidelines.
