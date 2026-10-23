# Changelog

## 1.0.0 — local dual-edition build / public code-only release

- Retain the existing 106-clip, 25,423-frame Full restoration from ef5bfb66.
- Restore the exact previous 723-frame Ultra asset baseline from 863353c5.
- Introduce explicit editions, independent package closures, install/config identities
  and embedded version/source/manifest fingerprints.
- Add bounded Full roaming using fixed-upstream stride curves and completed turns.
- Stop safely on missing action frames, retaining the last valid image.
- Verify real pointer pass-through, drag, menu exit and relaunch per edition.
- Retain failed experiments and distinguish CPU-time anomalies from cycle data.
- Publish source through a sanitized history without character material. Public
  dual binaries remain blocked by asset redistribution and library-source delivery gates.
