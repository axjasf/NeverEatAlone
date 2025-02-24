# Design Documentation Guide

## When to Create
- Before implementation starts
- When architectural decisions are made
- When patterns emerge

## Core Design Documents

### 1. ARCHITECTURE.md
```markdown
# [Feature] Architecture

## Overview
[One paragraph explaining the architectural approach]

## Key Decisions
1. [Decision Title]
   - Context: [What led to this]
   - Decision: [What we chose]
   - Rationale: [Why we chose it]

## Component Structure
[Key components and their relationships]

## Technical Boundaries
- Dependencies
- Integration points
- Constraints
```

### 2. SERVICE_*.md (For Services)
```markdown
# [Service Name]

## Purpose
[What this service handles]

## Interface
- Key methods
- Transaction boundaries
- Error handling

## Patterns Used
- Base patterns applied
- Service-specific patterns

## Examples
[Concrete usage examples]
```

## Examples
- See `docs/features/2-service-layer/design/SERVICE_ARCHITECTURE.md`
- See `docs/features/2-service-layer/design/SERVICE_BASE.md`
