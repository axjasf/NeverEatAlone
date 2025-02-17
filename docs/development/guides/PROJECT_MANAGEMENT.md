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
