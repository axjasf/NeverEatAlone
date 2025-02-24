# Change Request Process

## Overview
Change Requests (CRs) are organized under features in the `docs/features/` directory.

## Directory Structure
```
docs/features/
├── 1-data-model/              # Feature group
│   ├── OVERVIEW.md           # Feature summary
│   ├── design/               # Design decisions
│   └── crs/                  # Feature CRs
│       └── CR-YYYY.MM-N.md   # Individual CR
└── 2-service-layer/
    └── ...
```

## CR Creation Process
1. Create new branch: `feature/CR-YYYY.MM.DD-N-brief-description`
2. Create CR in appropriate feature directory: `docs/features/N-feature-name/crs/CR-YYYY.MM.DD-N.md`
3. Update feature OVERVIEW.md to include the new CR
4. Create design documents if needed

## 1. Change Request Types

### 1.1 Feature Changes
- New functionality
- Feature enhancements
- API additions

### 1.2 Bugfixes
- Error corrections
- Data inconsistency fixes
- Performance improvements

### 1.3 Refactoring
- Code restructuring
- Architecture improvements
- Technical debt reduction

### 1.4 Documentation
- Document updates
- Process improvements
- Template changes

## 2. CR Lifecycle

### 2.1 Creation Phase
1. Create new branch: `feature/CR-YYYY.MM.DD-N-brief-description`
2. Copy `CHANGE_REQUEST_TEMPLATE.md` to `docs/implementation/changes/CR-YYYY.MM.DD-N.md`
3. Fill out CR information and executive summary
4. Perform initial impact analysis
5. Create initial documentation update plan

### 2.2 Review Phase
1. Submit CR document for review
2. Address feedback on impact analysis
3. Refine documentation update plan
4. Get preliminary approval
5. Update CR status to "In Review"

### 2.3 Implementation Phase
1. Update CR status to "In Progress"
2. Follow documentation update sequence:
   - Functional Requirements
   - Architecture
   - Interfaces
   - Non-Functional Requirements
   - User Stories
   - Data Model
   - Implementation Details
3. Commit each documentation update separately
4. Implement changes following TDD
5. Update CR document with progress

### 2.4 Verification Phase
1. Complete all test requirements
2. Verify documentation updates
3. Perform technical review
4. Update CR status to "Completed"
5. Prepare release notes

## 3. Documentation Guidelines

### 3.1 Version Numbering
- Format: YYYY.MM.DD-N
- Increment N for multiple updates in one day
- All implementation docs share same version
- Include version history in each doc

### 3.2 Commit Messages
```
docs(scope): update [doc-name] for [CR-number]
feat(scope): implement [feature] for [CR-number]
fix(scope): resolve [issue] for [CR-number]
refactor(scope): improve [component] for [CR-number]
```

### 3.3 Branch Strategy
```
main
└── feature/CR-YYYY.MM.DD-N-description
    └── docs/CR-YYYY.MM.DD-N-description
```

## 4. Review Process

### 4.1 Documentation Review
1. Check completeness of all required sections
2. Verify cross-references
3. Validate version numbers
4. Check for technical accuracy

### 4.2 Technical Review
1. Verify test coverage
2. Check performance impact
3. Review security implications
4. Validate against requirements

### 4.3 Final Review
1. Complete verification checklist
2. Get required approvals
3. Prepare for merge
4. Update release documentation

## 5. Best Practices

### 5.1 Documentation Updates
1. Update one document at a time
2. Commit changes separately
3. Maintain cross-references
4. Keep version history current

### 5.2 Implementation
1. Follow TDD approach
2. Update tests first
3. Maintain backward compatibility
4. Document breaking changes

### 5.3 Review
1. Self-review before submission
2. Address all feedback
3. Keep CR document updated
4. Track all decisions

## 6. Templates and Examples

### 6.1 Available Templates
- `CHANGE_REQUEST_TEMPLATE.md`: Base template for all CRs
- `INTERACTION_TRACKING_REFACTOR.md`: Example of complex change
- `WORKING_NOTES.md`: Daily implementation notes

### 6.2 Example CR Numbers
- `CR-2024.02.13-1`: First CR of the day
- `CR-2024.02.13-2`: Second CR of the day

### 6.3 Example Commit Series
```bash
git commit -m "docs(cr): create CR-2024.02.13-1 for timezone handling"
git commit -m "docs(func): update requirements for CR-2024.02.13-1"
git commit -m "docs(arch): update architecture for CR-2024.02.13-1"
git commit -m "feat(model): implement timezone support for CR-2024.02.13-1"
```

## 7. Troubleshooting

### 7.1 Common Issues
1. Missing documentation updates
2. Incomplete impact analysis
3. Version number conflicts
4. Incomplete testing

### 7.2 Resolution Steps
1. Use documentation checklist
2. Review impact analysis guide
3. Follow version numbering rules
4. Complete test matrix

## 8. References

1. [BRD Structure](../../brd/README.md)
2. [Development Guidelines](../development/DEVELOPMENT.md)
3. [Testing Guidelines](../development/TESTING.md)
4. [Change Request Template](./CHANGE_REQUEST_TEMPLATE.md)
