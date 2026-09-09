# DNA Data Model (Informational Only)

> Original design goals, not implemented capabilities. See the [current capability matrix](../docs/capabilities.md) and [model definitions](../docs/models.md) before building.

- **Scope**: Digital storage of genomic *sequences* only (no procedures).
- **Encoding**: 2 bits/base (A,C,G,T). Human haploid ~3.2e9 bases ≈ 0.8 GB raw.
- **Compression**: Context models can reduce size further; plus metadata & integrity checks.
- **Ethics**: Strong privacy; do not store real data without consent.
