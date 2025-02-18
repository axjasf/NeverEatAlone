# Development Journal Structure

## Overview
This folder contains development journals tracking progress at sprint and feature levels. Each journal follows the branch it documents, enabling clear progress tracking and efficient information roll-up.

## File Organization
```
dev-journal/
├── README.md                                    # This file
├── _template.md                                 # Template for new journals
├── sprint-2025-02/                             # Current sprint folder
│   ├── DevJournal_Sprint-2025-02.md           # Sprint overview
│   ├── DevJournal_23-timezone.md              # Feature journals
│   ├── DevJournal_23.4-statement.md           # Sub-feature journals
│   └── DevJournal_35-blog.md                  # Feature journals
└── future-2025-Q1/                            # Future planning
    └── DevJournal_Future-2025-Q1.md           # Future plans
```

## Journal Types

### Sprint Journals
- Track sprint-level progress
- Roll up information from feature journals
- Located in sprint folder: `sprint-YYYY-MM/DevJournal_Sprint-YYYY-MM.md`
- Example: `sprint-2025-02/DevJournal_Sprint-2025-02.md`

### Feature Journals
- Track feature implementation
- Follow feature branches
- Located in sprint folder: `sprint-YYYY-MM/DevJournal_XX-name.md`
- Example: `sprint-2025-02/DevJournal_23-timezone.md`

### Sub-feature Journals
- Track component implementation
- Follow feature sub-branches
- Located in sprint folder: `sprint-YYYY-MM/DevJournal_XX.Y-name.md`
- Example: `sprint-2025-02/DevJournal_23.4-statement.md`

### Future Planning Journals
- Track future sprint planning
- Located in future folder: `future-YYYY-QN/DevJournal_Future-YYYY-QN.md`
- Example: `future-2025-Q1/DevJournal_Future-2025-Q1.md`

## Version Format
- `YYYY.MM.DD-VERSION-branch-id`
- Examples:
  - `2025.02.17-6-sprint-02`
  - `2025.02.17-6-feat-23`
  - `2025.02.17-6-feat-23.4`

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
### 2025.02.17-1
- ✅ Initial setup complete
- ✅ Core implementation
- Started documentation
```

## Maintenance
1. Create journals when:
   - Starting a new sprint (create sprint folder and overview journal)
   - Creating a feature branch (in current sprint folder)
   - Creating a sub-feature branch (in current sprint folder)

2. Update journals when:
   - Making technical decisions
   - Completing work items (mark with ✅)
   - Preparing for merges

3. Close journals when:
   - Sprint completes (archive sprint folder)
   - Feature merges
   - Branch closes
