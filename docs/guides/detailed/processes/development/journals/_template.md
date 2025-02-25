# Development Journal - [branch-name]
Version: YYYY.MM.DD-N-branch-id

<!--
See _examples.md for concrete examples and best practices of development journals.
See PROCESS.md for detailed process guidelines.

JOURNAL TYPES:
1. Sprint Journals (sprint-YYYY-MM/DevJournal_Sprint-YYYY-MM.md)
   - Track sprint-level progress
   - Roll up information from feature journals
   Example: sprint-2025-02/DevJournal_Sprint-2025-02.md

2. Feature Journals (sprint-YYYY-MM/DevJournal_XX-name.md)
   - Track feature implementation
   - Follow feature branches
   Example: sprint-2025-02/DevJournal_23-timezone.md

3. Sub-feature Journals (sprint-YYYY-MM/DevJournal_XX.Y-name.md)
   - Track component implementation
   - Follow feature sub-branches
   Example: sprint-2025-02/DevJournal_23.4-statement.md

KEY GUIDELINES:
1. Fixed Sections (in order):
   Feature Journal Structure:
   - Status Summary: Phase, progress, quality, risks, dependencies
   - Current Focus: Active work, challenges, dependencies
   - Next Steps: Immediate tasks, upcoming work
   - Technical Progress: Implementation status, test status
   - Technical Decisions: Key architectural and technical choices
   - History: Newest entries first, with concrete technical details

   Sprint Journal Structure:
   - Status Summary: Overall sprint health
   - Current Focus: Status per feature, with active challenges
   - Next Steps: Sprint-level priorities
   - Technical Progress: Cross-feature implementation, patterns
   - Technical Decisions: Architecture evolution, shared patterns
   - Sprint Learnings: Cross-feature insights
   - History: Oldest first, tracking feature flow

2. Symbols and Usage:
   ✅ = Completed item (always at start of line)
   [ ] = Planned/in-progress item (only for concrete items)
   💡 = Technical learning/insight (used in History)
   🔄 = Future consideration/evolution point
   🔵 = Branch creation (sprint journals)
   🔹 = Branch merge (sprint journals)

   Rules:
   - Symbols always go at the start of lines
   - Don't mix symbols in section headers
   - Leave items without symbols if they're just descriptive
   - History entries focus on completed work (✅), learnings (💡), and evolution points (🔄)

3. Keep entries:
   - Focused on what matters technically
   - Concrete and specific
   - Free of routine progress
   - Updated with significant decisions
-->

## Status Summary
- Phase: [Implementation/Testing/Review]
- Progress: [On track/Delayed/Blocked]
- Quality: [Green/Yellow/Red]
- Risks: [None/Listed]
- Dependencies: [Met/Pending]

## Current Focus
### Active Components
- ✅ Completed components
- [ ] In-progress components
- Planned components

### Challenges
- Active blockers
- Technical challenges
- Dependencies

## Next Steps
### Immediate Tasks
- [ ] Next concrete actions
- [ ] Dependencies to resolve

### Planning
- [ ] Upcoming work
- 🔄 Future considerations

## Technical Progress
### Implementation Status
- ✅ Completed items
- [ ] In-progress items
- 💡 Technical learnings
- 🔄 Future considerations

### Test Status
- ✅ Completed test items
- [ ] Planned test items
- 💡 Test insights
- 🔄 Test evolution points

## Technical Decisions
- ✅ Decisions made
- 💡 Implementation insights
- 🔄 Evolution points

## Sprint Learnings
[Sprint journals only]
- 💡 Cross-feature patterns
- 💡 Technical insights
- 🔄 Evolution considerations

## History
### YYYY.MM.DD-N-branch-id
- ✅ Key completions
- 💡 Technical learnings
- 🔄 Future considerations
- 🔵/🔹 Branch points (sprint journals)
