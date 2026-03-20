# SMB Cash Flow Risk — Execution Pipeline

This document explains how work on `smb-cashflow-risk` should be carried through from idea to shipped improvement.

## Core principle
Every meaningful change should move through a consistent sequence:
1. clarify the outcome
2. define the scope and constraints
3. create a concrete implementation blueprint
4. implement the change
5. test it
6. simplify where possible
7. validate the final result before merge

## What good execution looks like
A change is considered complete only when:
- the intended user or demo outcome is clear
- the diff is focused and understandable
- tests or smoke checks pass
- documentation and code do not contradict each other
- the repo becomes easier to understand, not harder

## Expected planning inputs
Before implementation starts, the work should be clear about:
- the problem being solved
- the visible artifact that proves success
- the inputs/data it depends on
- what is explicitly out of scope
- what should be tested before merge

## Expected review standard
Before merge, every substantial change should be checked for:
- correctness
- regressions
- operational assumptions
- documentation accuracy
- portfolio/demo quality
- honest framing of any ML claims or limitations

## Current project expectation
This repo should prefer:
- small, scoped changes when possible
- explicit docs when behavior or positioning changes
- honest reporting over inflated claims
- release readiness through repeatable validation, not last-minute improvisation
