# Development Journal Structure

## Overview
This folder contains development journals tracking progress at sprint and feature levels. Each journal follows the branch it documents, enabling clear progress tracking and efficient information roll-up.

## File Organization
```
dev-journal/
├── README.md                          # This file
├── DevJournal_Sprint-YYYY-MM.md      # Sprint journals (e.g., DevJournal_Sprint-2024-02.md)
├── features/                          # Feature-specific journals
│   ├── DevJournal_XX-name.md         # Feature journals (e.g., DevJournal_23-timezone.md)
│   └── DevJournal_XX.Y-name.md       # Sub-feature journals (e.g., DevJournal_23.4-statement.md)
└── _template.md                       # Template for new journals
```

## Journal Types

### Sprint Journals
- Track sprint-level progress
- Roll up information from feature journals
- Name format: `DevJournal_Sprint-YYYY-MM.md`
- Example: `DevJournal_Sprint-2024-02.md`

### Feature Journals
- Track feature implementation
- Follow feature branches
- Name format: `DevJournal_XX-name.md`
- Example: `DevJournal_23-timezone.md`

### Sub-feature Journals
- Track component implementation
- Follow feature sub-branches
- Name format: `DevJournal_XX.Y-name.md`
- Example: `DevJournal_23.4-statement.md`

## Version Format
- `YYYY.MM.DD-VERSION-branch-id`
- Examples:
  - `2024.02.17-6-sprint-02`
  - `2024.02.17-6-feat-23`
  - `2024.02.17-6-feat-23.4`

## Section Structure
### Current Focus [branch-id]
- Parent feature headline
- Current activity subheadline
- Implementation points
Example:
```markdown
### Feature Implementation
- ✅ Initial setup complete
- Current task in progress
- Next task planned
```

### Progress & Decisions [branch-id]
- Implementation status with completion indicators
- Technical decisions with rationale
- Challenges & solutions
Example:
```markdown
### Implementation Status
1. Core Implementation (40%)
   - ✅ Initial setup complete
   - ✅ Base structure defined
   - Current progress
```

### Next Steps [branch-id]
- Upcoming work with checkboxes
- Dependencies
- Blockers
Example:
```markdown
- [ ] Major Task
  - [✅] Completed sub-task
  - [ ] Current sub-task
```

### Status [branch-id]
- Implementation progress percentage
- Test coverage status
- Documentation status
Example:
```markdown
- Implementation: 80%
- Test Coverage: ✅ Complete
- Documentation: Current
```

### Merge Notes [branch-id]
- Key points for parent branch
- Technical decisions to preserve
- Technical debt status
Example:
```markdown
- ✅ Core implementation complete
- ✅ No technical debt
- Documentation current
```

### History [branch-id]
- Version-based entries with completion status
- Key changes and decisions
- Progress milestones
Example:
```markdown
### 2024.02.17-1
- ✅ Initial setup complete
- ✅ Core implementation
- Started documentation
```

## Maintenance
1. Create journals when:
   - Starting a new sprint
   - Creating a feature branch
   - Creating a sub-feature branch

2. Update journals when:
   - Making technical decisions
   - Completing work items (mark with ✅)
   - Preparing for merges

3. Close journals when:
   - Sprint completes
   - Feature merges
   - Branch closes
