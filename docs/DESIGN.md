# Memory Court

Agent memory that can explain, dispute, expire and retract what it believes.

## Problem

Agents can retain stale or conflicting information long after the original evidence changed.

## Approach

Store claims with source IDs, observation time, validity interval and status. Keep an append-only revision log. Detect structured conflicts and require resolution or abstention; add semantic claim extraction later.

## Demo concept

An assistant remembers an old shipping address. A conflicting update arrives, its source is later retracted, and the memory view explains exactly which fact is currently supported.

## First implementation

SQLite claim store with immutable events, expiry, conflict detection for entity/attribute pairs, retraction and evidence-linked retrieval. Use invented identities only.

## Evaluation

Measure stale-memory use, conflict detection, unsupported answers and successful retraction across time-based test sequences. Never claim that provenance proves source truth.

## Milestones

1. Temporal claim store and adversarial sequence tests
2. Retrieval with evidence and explicit abstention
3. Optional LLM extraction adapter with structured validation
4. Interactive dispute timeline and benchmark against last-write-wins memory

## Your contribution

Provide invented examples of facts that change or conflict in a workflow you understand.

## Status and license

Design brief only; no implementation or measured results yet. Original code will use GPL-3.0-only.
