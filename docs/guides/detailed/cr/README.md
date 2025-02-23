# Change Request Management

## Directory Structure
This directory contains all Change Requests (CRs) for the project, organized by their current status:

1. **📋 1-backlog/**
   - CRs that are defined but not yet ready for implementation
   - Initial specifications and planning documents
   - Matches GitHub project "Backlog" column

2. **🎯 2-sprint-backlog/**
   - CRs selected for current sprint
   - Fully specified and ready for implementation
   - Matches GitHub project "Sprint Backlog" column

3. **💻 3-in-progress/**
   - CRs actively being worked on
   - Has assigned developer and associated branch
   - Matches GitHub project "In Progress" column

4. **👀 4-in-review/**
   - CRs with PRs waiting for review
   - CRs in testing phase
   - Matches GitHub project "In Review" column

5. **✅ 5-done/**
   - Completed and deployed CRs
   - Organized by year/month
   - Matches GitHub project "Done" column

## CR Lifecycle
1. CR is created from TEMPLATE.md and placed in `1-backlog/`
2. During sprint planning, moved to `2-sprint-backlog/`
3. When work begins, moved to `3-in-progress/`
4. When PR is created, moved to `4-in-review/`
5. When completed, moved to `5-done/YYYY/MM/`

## File Naming Convention
- Format: `CR-YYYY.MM-N.md`
- Example: `CR-2024.02-23.md`

## Status Tracking
- Each CR's status in this directory structure should match its GitHub issue status
- Use `scripts/cr.sh` to manage CRs and keep statuses in sync
- Regular cleanup ensures only active CRs remain in 1-4 directories
