# Changelog

## 1.0.1 — exact-frame packaging optimization

- Store each byte-identical frame once within its clip, with a build-time index:
  Core 2,651 logical / 2,531 physical frames; Ultra 723 logical / 686 physical frames.
  Original 24 fps, offsets, alpha, decoded Qt pixels and all actions remain unchanged.
- Exclude the unused optional Python `_hashlib` OpenSSL backend. Python 3.12 uses
  builtin `_sha2` for random seeding; no Qt DLL, image plugin or license text is removed.
- About 5.17% / 6.21% smaller Core / Ultra downloads and 9.72 / 6.71 MB less unpacked
  storage than v1.0.0. This is a packaging benefit, not a CPU or energy-saving claim.
- Add all-frame Qt pixel/recovery tests, full PE closure checks and matched binary
  A/B evidence. Final ZIP identity and desktop results are in RELEASE-VALIDATION.json.
- Keep the existing 40 MiB cache, QImage renderer and timer. Long soak remains
  SKIPPED_BY_USER; high DPI, 4K, multi-monitor, GPU, watts and Present are unverified.

## 1.0.0 — Core and Ultra

- Core is the official eleven-animation base set (2,651 frames), with bounded
  movement and turns. Ultra retains three animations (723 frames).
- Both editions are standalone and have separate resources, identity and settings.
- Remove unused Qt translation payloads without changing images or playback.
- Preserve lossless frames and the original 24 fps timeline; keep bounded idle cache.
- Add source delivery for LGPL libraries and authorized non-commercial asset terms.
- Correct the previous comparison: the official 348.97 MB base ZIP embeds eleven
  clips; the other 95 upstream animations use separate packs.

## Historical v1.0.0-code-only

The prior prerelease remains unchanged as history. It had no public binary packages
and discussed Full 106 / Ultra 3 local experiments. Its official-base full-library
label was incorrect and is superseded by the current audited scope.
