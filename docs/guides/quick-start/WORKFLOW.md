# Quick Start Workflow Guide

## When to Do What

### Feature Lifecycle
1. **Starting Feature**
   - Create feature structure & docs
   - Define scope & architecture
   → See: `../detailed/processes/features/lifecycle/PLANNING.md`

2. **Making Changes**
   - Create CR & branch
   - Start tracking in DevJournal
   → See: `../detailed/processes/features/changes/CR_QUICK.md`

3. **Development Tracking**
   Time-based:
   - Morning: Plan in DevJournal
   - Evening: Document progress

   Change-based:
   - Pre-commit: Record decisions (💡)
   - Post-commit: Update progress
   → See: `../detailed/processes/development/journals/PROCESS.md`

4. **Completing Work**
   - Update all documentation
   - Create pull request
   → See: `../detailed/processes/features/lifecycle/COMPLETION.md`

5. **Sprint Management**
   - Create sprint documentation
   - Update feature statuses
   → See: `../detailed/processes/development/sprints/PLANNING.md`

## When to Update What

### Core Documents
1. **Feature OVERVIEW.md**
   - On creating feature folder
   - On feature scope change
   - On feature completion

2. **CR Documents**
   - On change proposal
   - On major progress
   - On completion

3. **DevJournal**
   - Daily planning
   - Key decisions (💡)
   - Progress updates

4. **Design Docs**
   - Before implementation
   - On pattern discovery
   - On architecture change
   → See: `../detailed/processes/features/documentation/DESIGN_DOCS.md`

### Key Locations
1. **Features** (`docs/features/N-feature-name/`)
   - `OVERVIEW.md`
   - `design/ARCHITECTURE.md`
   - `crs/CR-YYYY.MM-NN.md`

2. **Progress** (`docs/dev-journal/`)
   - `sprint-YYYY-MM/DevJournal_*.md`
   - GitHub Issues & Board

For detailed instructions, see `guides/detailed/processes/`
For commands, see `COMMANDS.md`
