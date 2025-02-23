# Project Management Guide

## Project Structure
```
docs/
├── features/                # Feature documentation
│   ├── 1-data-model/       # First milestone
│   └── 2-service-layer/    # Second milestone
├── dev-journal/            # Development journals
│   └── sprint-YYYY-MM/     # Sprint journals
└── guides/                # Development guides
    ├── quick-start/       # Daily essentials
    └── detailed/         # In-depth docs
```

## Feature Management

### Feature Lifecycle
1. **Planning**
   - Create feature directory
   - Create OVERVIEW.md
   - Plan initial CRs
   - Create design documents

2. **Implementation**
   - Create CRs in feature's crs/
   - Follow TDD process
   - Update documentation
   - Track in dev journal

3. **Completion**
   - Verify all CRs done
   - Update OVERVIEW.md
   - Archive documentation

## Change Request (CR) Process

### CR Structure
```
features/N-feature-name/
├── OVERVIEW.md           # Feature summary
├── design/              # Design decisions
└── crs/                # Change requests
    └── CR-YYYY.MM-N.md  # Individual CR
```

### CR Lifecycle
1. **Creation**
   - Create GitHub issue
   - Create CR document
   - Create feature branch
   - Update documentation

2. **Implementation**
   - Follow TDD process
   - Update CR status
   - Document decisions
   - Track progress

3. **Review**
   - Code review
   - Documentation review
   - Update CR status
   - Create PR

4. **Completion**
   - Merge PR
   - Finalize CR
   - Update documentation

## Development Journal

### Journal Types
1. **Sprint Journals**
   - Sprint overview
   - Feature progress
   - Technical decisions
   - Sprint learnings

2. **Feature Journals**
   - Implementation details
   - Technical decisions
   - Progress tracking
   - Future considerations

### Journal Structure
```
dev-journal/
├── sprint-YYYY-MM/
│   ├── DevJournal_Sprint-*.md    # Sprint overview
│   └── DevJournal_Feature-*.md   # Feature details
└── future-YYYY-QN/
    └── DevJournal_Future-*.md    # Future planning
```

## Best Practices

### Documentation
1. **Version Control**
   - Use YYYY.MM.DD-N format
   - Update all related docs
   - Keep history in each doc
   - Cross-reference changes

2. **Organization**
   - One CR per significant change
   - Clear feature boundaries
   - Consistent structure
   - Regular updates

3. **Progress Tracking**
   - Update journals daily
   - Track decisions
   - Document insights
   - Note future points

See `quick-start/` directory for day-to-day commands and workflows.
