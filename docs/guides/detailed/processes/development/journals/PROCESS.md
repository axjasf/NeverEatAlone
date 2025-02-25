# Development Journal Process

## Overview
Development journals track progress and decisions at different levels. Small feature branches keep journals concise while maintaining the core structure. When merging, insights cascade up:
- Feature branch journals (e.g., 45-base-service) → Parent feature journals (e.g., 44-service-layer) → Sprint journals
- Technical learnings (💡) and patterns flow upward during merges
- Each level adds broader context while preserving key insights

## When to Update
1. Time-based
   - Morning: Plan work
   - Evening: Record progress

2. Change-based
   - Pre-commit: Record decisions
   - Post-commit: Update progress

## Version Format
```
YYYY.MM.DD-N-branch-id
```
Where:
- N: Sequential number for each commit of this document
- branch-id: Short branch identifier
Example: 2025.02.23-3-base-service

## What to Record
1. Technical Decisions (💡)
   - Architecture choices
   - Pattern discoveries
   - Implementation approaches

2. Future Points (🔄)
   - Improvement ideas
   - Technical debt
   - Evolution plans

3. Progress
   - Completed items
   - Blockers encountered
   - Next steps

See `TEMPLATE.md` for journal structure.

## Structure Requirements
1. **Status Summary**
   - Branch name and status
   - Current phase
   - Parent CR/feature
   - Dependencies

2. **Current Focus**
   - Implementation progress
   - Concrete next steps
   - Clear action items

3. **Technical Content**
   - Implementation insights
   - Code patterns
   - Test approaches
   - Learnings for reuse

## Best Practices
1. **Clarity**
   - Use emoji markers consistently
   - Keep next steps actionable
   - Link to relevant CRs/docs
   - Track dependencies

2. **Progress**
   - Update status after each commit
   - Record all technical decisions
   - Note pattern discoveries
   - Plan next concrete steps

3. **History**
   - Keep versions sequential
   - Record key completions
   - Note technical insights
   - Track evolution points
