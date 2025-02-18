# Project Management Guide

## Overview
This guide describes our project management workflow, from idea to implementation. It includes our GitHub Projects setup, Change Request (CR) process, and branching strategy.

## Project Board Structure

### Columns
1. **📋 Backlog**
   - New issues that are defined but not yet ready
   - Initial ideas and feature requests
   - Automatically receives new issues

2. **🎯 Sprint Backlog**
   - Issues selected for current sprint
   - Moved here during sprint planning
   - Fully specified and ready to work on

3. **💻 In Progress**
   - Issues actively being worked on
   - Has assigned developer
   - Has associated branch and CR

4. **👀 In Review**
   - PRs waiting for review
   - Issues in testing phase
   - Automatically updated by PR creation

5. **✅ Done**
   - Completed and deployed issues
   - Automatically updated by PR merge

## Change Request (CR) Process

### CR Directory Structure
CRs are organized in `docs/implementation/changes/` to match the project board:

1. **1-backlog/**
   - CRs that are defined but not yet ready
   - Matches "Backlog" column

2. **2-sprint-backlog/**
   - CRs selected for current sprint
   - Matches "Sprint Backlog" column

3. **3-in-progress/**
   - CRs actively being worked on
   - Matches "In Progress" column

4. **4-in-review/**
   - CRs with PRs waiting for review
   - Matches "In Review" column

5. **5-done/YYYY/MM/**
   - Completed CRs by year/month
   - Matches "Done" column

### CR Creation Flow
1. Create GitHub issue
2. Create CR document from TEMPLATE.md
3. Create feature branch
4. Update Implementation Plan
5. Update Working Notes

### Example Story: Adding Timezone Support
```bash
# 1. Create issue and CR
./scripts/cr.sh create "Implement timezone handling" "Add timezone support..." "feature"

# 2. Update progress
./scripts/cr.sh update 23 "in-progress" "Started implementing TimezoneAwareBase"

# 3. Finalize CR
./scripts/cr.sh finalize 23 "CR-2024.02-23"
```

### CR Document Structure
- Issue information
- Requirements analysis
- Implementation plan
- Test plan
- Documentation updates
- Review checklist

## Branching Strategy

### Branch Naming Convention
- Feature: `feature/<issue-number>-<description>`
- Bugfix: `bugfix/<issue-number>-<description>`
- Documentation: `docs/<issue-number>-<description>`
- Refactor: `refactor/<issue-number>-<description>`

### Example:
```bash
# For issue #23: Implement timezone handling
git checkout -b feature/23-implement-timezone-handling
```

## Implementation Flow

### Example Story: New Feature Implementation

1. **Initial Setup**
   ```bash
   # Create issue and CR
   ./scripts/cr.sh create "Add contact search" "Implement contact search..." "feature"
   ```

2. **Start Implementation**
   ```bash
   # Move issue to In Progress
   # Update CR status
   ./scripts/cr.sh update 24 "in-progress" "Starting TDD cycle for search functionality"
   ```

3. **Development Cycle**
   ```bash
   # Write tests
   # Implement feature
   # Update documentation
   ./scripts/cr.sh update 24 "in-review" "Ready for code review"
   ```

4. **Completion**
   ```bash
   # After PR approval and merge
   ./scripts/cr.sh finalize 24 "CR-2025.02.17-1"
   ```

## Documentation Structure

### Core Tools
1. **GitHub Project Board**
   - Visual task tracking
   - Current status at a glance
   - Simple kanban: Backlog → In Progress → Done

2. **CR Documents** (`docs/implementation/changes/`)
   - One document per significant change
   - Requirements and implementation notes
   - Created via `./scripts/cr.sh create`

3. **Development Journal** (`docs/implementation/DEVELOPMENT_JOURNAL.md`)
   - Combined implementation plan and working notes
   - Tracks current sprint progress and decisions
   - Fine-granular observations and progress tracking
   - Format:
     ```markdown
     # Development Journal
     Version: YYYY.MM.DD-N

     ## Current Focus
     What the sprint is focusing on right now

     ## What I'm Working On
     Current implementation tasks and progress

     ## Recent Progress
     Completed items and achievements

     ## Technical Decisions
     Architecture and implementation choices

     ## Next Steps
     Immediate tasks and plans

     ## Backlog
     Future work items with priorities

     ## History
     Version changelog
     ```

4. **Development Journal Management**

### Sprint Branch Workflow
1. Each sprint has a dedicated branch (`sprint/YYYY-MM`)
   - Contains the single source of truth for development journal
   - All feature branches branch from here

2. Feature Branch Process
   - Branch from current sprint branch
   - Update development journal in sprint branch
   - All progress tracked in sprint branch journal

3. Sprint Completion
   - Sprint branch merges to main
   - New sprint branch created
   - Ongoing features rebase onto new sprint branch

4. Journal Structure
   - Current Focus: What the sprint is focusing on right now
   - What I'm Working On: Current implementation tasks
   - Recent Progress: Completed items and achievements
   - Technical Decisions: Architecture and implementation choices
   - Next Steps: Immediate tasks and plans
   - Backlog: Future work items with priorities
   - History: Version changelog

### Simple Workflow
1. **Starting Work**
   ```bash
   # Create issue and CR
   ./scripts/cr.sh create "Add feature X" "Description" "feature"

   # Update journal
   # Make updates in sprint branch's DEVELOPMENT_JOURNAL.md
   ```

2. **Progress Updates**
   - Move cards on project board
   - Update development journal with progress
   - Update CR if major milestone or major insights relevant to the CR

3. **Completing Work**
   ```bash
   # Finalize CR
   ./scripts/cr.sh finalize <issue-number> <cr-number>

   # Add completion to journal
   # Document completion in sprint branch's DEVELOPMENT_JOURNAL.md
   ```

## Best Practices

### Issue Management
1. **Creation**
   - Clear, descriptive title
   - Detailed description
   - Appropriate labels
   - Linked to CR when applicable

2. **Progress Tracking**
   - Regular status updates
   - Clear acceptance criteria
   - Documentation kept up to date

3. **Completion**
   - All tests passing
   - Documentation updated
   - CR finalized
   - PR reviewed and merged

### Example: Full Feature Lifecycle

Let's follow a complete example of implementing a new feature:

1. **Feature Inception**
   ```
   Idea: We need contact search functionality
   ```

2. **Issue Creation**
   ```
   Title: Implement contact search
   Description: Add ability to search contacts by name and tags
   Label: feature
   ```

3. **CR Creation**
   ```bash
   ./scripts/cr.sh create "Implement contact search" "Add search..." "feature"
   # Creates:
   # - Issue #24
   # - CR-2025.02.17-1
   # - Branch feature/24-implement-contact-search
   ```

4. **Implementation**
   ```bash
   # Start work
   ./scripts/cr.sh update 24 "in-progress" "Starting implementation"

   # Regular updates
   ./scripts/cr.sh update 24 "in-progress" "Completed search API"
   ./scripts/cr.sh update 24 "in-progress" "Added UI components"

   # Ready for review
   ./scripts/cr.sh update 24 "in-review" "Ready for testing"
   ```

5. **Completion**
   ```bash
   # After successful review and merge
   ./scripts/cr.sh finalize 24 "CR-2025.02.17-1"
   ```

## Common Tasks Reference

### Creating a New Feature
1. Create issue in GitHub
2. Use `./scripts/cr.sh create` to set up CR
3. Follow TDD process
4. Keep documentation updated
5. Create PR when ready
6. Finalize CR after merge

### Updating Progress
1. Use `./scripts/cr.sh update` for status changes
2. Update development journal in sprint branch
3. Document technical decisions and progress

### Code Review Process
1. Create PR
2. Link to issue and CR
3. Update issue status to "In Review"
4. Address review comments
5. Get approval
6. Merge and finalize CR

## Pattern Evolution Process

### Overview
Pattern evolution occurs when we discover better ways to implement or test features. This process ensures improvements are systematically applied across the codebase.

### Pattern Discovery Flow
1. **Discovery and Documentation**
   ```bash
   # 1. Document new pattern
   ./scripts/cr.sh update <cr-number> "in-progress" "Discovered improved pattern for <area>"

   # 2. Update pattern guide
   # Example: Update TEST_PATTERNS.md with new test pattern
   ```

2. **Impact Analysis**
   - Identify affected components
   - Assess urgency:
     - High: Security/correctness issues
     - Medium: Significant improvements
     - Low: Style/readability improvements
   - Create backport tasks
   - Set timeline for consistency

3. **Implementation Planning**
   ```bash
   # Create backport CR
   ./scripts/cr.sh create "Backport <pattern> to existing components" "..." "refactor"

   # Link to original CR
   ./scripts/cr.sh link <original-cr> <backport-cr>
   ```

### Pattern Consistency Checks

#### Regular Reviews
1. **Sprint Planning**
   - Review pattern consistency status
   - Prioritize critical pattern alignments
   - Schedule pattern alignment sprints

2. **Code Review**
   - Check for pattern adherence
   - Identify pattern deviations
   - Document new pattern discoveries

3. **Automated Checks**
   - Pattern violation detection
   - Test coverage for pattern requirements
   - Pattern consistency metrics

#### Example: Test Pattern Evolution
```bash
# 1. Pattern Discovery
./scripts/cr.sh update 23 "in-progress" "Discovered better timezone test patterns"

# 2. Document Pattern
# Update TEST_PATTERNS.md

# 3. Create Backport Tasks
./scripts/cr.sh create "Backport timezone test patterns" "Apply improved patterns..." "refactor"

# 4. Track Progress
./scripts/cr.sh update <backport-cr> "in-progress" "Updating Contact BO tests"
```

### Pattern Evolution Checklist
1. **Discovery Phase**
   - [ ] Document new pattern
   - [ ] Update relevant guides
   - [ ] Assess impact and urgency
   - [ ] Create backport tasks

2. **Planning Phase**
   - [ ] Set consistency timeline
   - [ ] Prioritize backport tasks
   - [ ] Schedule pattern alignment
   - [ ] Update sprint planning

3. **Implementation Phase**
   - [ ] Create backport CR
   - [ ] Update affected components
   - [ ] Verify pattern consistency
   - [ ] Update documentation

4. **Verification Phase**
   - [ ] Run automated checks
   - [ ] Conduct pattern review
   - [ ] Verify all components
   - [ ] Update status tracking

### Best Practices

1. **Pattern Documentation**
   - Clear, concise pattern description
   - Example implementations
   - Migration guidelines
   - Known limitations

2. **Consistency Management**
   - Regular pattern audits
   - Automated consistency checks
   - Pattern evolution tracking
   - Clear timeline for alignment

3. **Implementation Strategy**
   - Prioritize by impact
   - Incremental updates
   - Verify each change
   - Maintain traceability

4. **Review Process**
   - Pattern adherence checks
   - Consistency verification
   - Documentation updates
   - Knowledge sharing

### Example Story: Test Pattern Evolution

1. **Discovery**
   ```bash
   # Document discovery in CR
   ./scripts/cr.sh update 23 "in-progress" "Found better timezone test patterns:
   1. UTC moment-based comparisons
   2. DST transition handling
   3. Edge case coverage"
   ```

2. **Documentation**
   ```bash
   # Update pattern guide
   # Add to TEST_PATTERNS.md:
   # - New pattern description
   # - Migration guidelines
   # - Example implementations
   ```

3. **Planning**
   ```bash
   # Create backport CR
   ./scripts/cr.sh create "Backport timezone patterns" "Apply improved patterns..." "refactor"

   # Update sprint planning
   # Add to next sprint's backlog
   ```

4. **Implementation**
   ```bash
   # Start backport
   ./scripts/cr.sh update <backport-cr> "in-progress" "Updating Contact BO tests"

   # Track progress
   ./scripts/cr.sh update <backport-cr> "in-progress" "2/3 BOs updated"
   ```

### Troubleshooting

1. **Pattern Conflicts**
   - Document conflicts
   - Resolve through team review
   - Update pattern guide
   - Communicate changes

2. **Implementation Challenges**
   - Break down into smaller tasks
   - Focus on high-impact changes
   - Maintain incremental progress
   - Regular status updates

3. **Consistency Issues**
   - Run automated checks
   - Review pattern adherence
   - Update documentation
   - Schedule alignment sprints

## Troubleshooting

### Common Issues
1. **Branch Creation Failed**
   ```bash
   # Solution: Commit or stash changes first
   git stash
   ./scripts/cr.sh create "..."
   ```

2. **CR Update Failed**
   ```bash
   # Solution: Check issue number and status
   ./scripts/cr.sh update <correct-number> <valid-status> "message"
   ```

### Getting Help
- Check this guide
- Review existing CRs for examples
- Ask for help in team chat
