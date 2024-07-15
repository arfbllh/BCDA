# ADR-0002 Split Storage SQL and Parquet

## Status
Accepted

## Context
cBioPortal-style matrix files (mRNA, methylation, CNA) are wide and large, while metadata/clinical entities are relational.

## Decision
Use relational DB for transactional and metadata entities; use Parquet/object storage for wide matrix datasets.

## Consequences
- Better query performance and storage efficiency for matrix slices
- Additional operational complexity (object storage and parquet query layer)
- Cleaner scaling path for high-throughput ingestion
