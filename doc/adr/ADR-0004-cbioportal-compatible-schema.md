# ADR-0004 cBioPortal-Compatible Schema

## Status
Accepted

## Context
Input data follows cBioPortal conventions (`meta_*`, `data_*`, `case_lists`).

## Decision
Adopt a logical schema that preserves study metadata and supports dynamic clinical attributes while keeping `type_of_cancer` first-class.

## Consequences
- Easier ingestion from public cBioPortal-like studies
- Smooth extension from breast-only data to broader cancer data later
