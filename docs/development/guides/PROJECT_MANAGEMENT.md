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

### CR Creation Flow
1. Create GitHub issue
2. Create CR document
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
./scripts/cr.sh finalize 23 "CR-2025.02.16-1"
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

3. **Development Journal** (`docs/implementation/WORKING_NOTES.md`)
   - Combined implementation plan and working notes
   - Informal, chronological entries
   - Daily updates and decisions
   - Format:
     ```markdown
     # Development Journal

     ## Current Focus (Updated: YYYY-MM-DD)
     What I'm working on right now and why

     ## Recent Updates
     ### YYYY-MM-DD
     - What I did
     - Decisions made
     - Next steps

     ## Backlog
     Things I want to do next, in rough priority order
     ```

### Simple Workflow
1. **Starting Work**
   ```bash
   # Create issue and CR
   ./scripts/cr.sh create "Add feature X" "Description" "feature"

   # Update journal
   echo "Starting work on feature X..." >> docs/implementation/WORKING_NOTES.md
   ```

2. **Daily Updates**
   - Move cards on project board
   - Add journal entry with progress
   - Update CR if major milestone

3. **Completing Work**
   ```bash
   # Finalize CR
   ./scripts/cr.sh finalize <issue-number> <cr-number>

   # Add completion note
   echo "Completed feature X" >> docs/implementation/WORKING_NOTES.md
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
2. Keep Working Notes updated
3. Update Implementation Plan as needed

### Code Review Process
1. Create PR
2. Link to issue and CR
3. Update issue status to "In Review"
4. Address review comments
5. Get approval
6. Merge and finalize CR

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
