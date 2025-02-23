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
- `YYYY.MM.DD-N-branch-id` (N is a simple counter)
- Examples:
  - `2025.02.17-1-sprint-02`
  - `2025.02.17-2-feat-23`
  - `2025.02.17-3-feat-23.4`

## Symbol Usage
### Core Symbols
- ✅ = Completed items (always at start of line)
- [ ] = Only for concrete planned/in-progress items
- 🔄 = Future integration points/architectural evolution ideas
- 💡 = Specific technical insights/learnings (used in History)

### Usage Rules
- Symbols always go at the start of lines
- Don't mix symbols in section headers
- Leave items without symbols if they're just descriptive
- History entries focus on completed work (✅), learnings (💡), and evolution points (🔄)

## Section Structure
The following sections are fixed and should not be modified:

### Current Focus [branch-id]
- Parent feature reference
- Completed and in-progress components
- Active development points
Example:
```markdown
#### Completed Components
- ✅ Component A: Complete
- [ ] Component B: In Progress
- Component C: Not Started
```

### Progress & Decisions [branch-id]
- Implementation status with completion indicators
- Technical decisions with rationale
- Evolution considerations
Example:
```markdown
1. Core Implementation
   - ✅ Initial setup complete
   - [ ] Current focus
   - 🔄 Evolution Points:
     * Specific consideration
```

### Next Steps [branch-id]
- Immediate next tasks
- Dependencies
Example:
```markdown
- [ ] Immediate Next Task
  - ✅ Completed prerequisite
  - [ ] Current focus
```

### Status [branch-id]
- Qualitative implementation status
- Test coverage assessment
- Documentation status
Example:
```markdown
- Implementation: In Progress/Complete
- Test Coverage: Adequate/Needs Work
- Documentation: Current/Needs Update
```

### History [branch-id]
- Newest entries first
- Focus on what mattered technically
- Capture learnings and evolution points
Example:
```markdown
### YYYY.MM.DD-N-branch-id
- ✅ Major milestone achieved
- 💡 Specific technical insight
- 🔄 Next: Evolution consideration
```

## Maintenance
1. Create journals when:
   - Starting a new sprint
   - Creating a feature branch
   - Creating a sub-feature branch

2. Update journals when:
   - Making significant technical decisions
   - Completing meaningful work items
   - Discovering important technical insights
   - Identifying evolution points

3. Close journals when:
   - Sprint completes
   - Feature merges
   - Branch closes

## Key Principles
1. Keep entries focused and meaningful
2. Emphasize technical insights over routine progress
3. Use history to track what actually mattered
4. Maintain fixed document structure
5. Use symbols consistently
6. Focus on concrete technical aspects
