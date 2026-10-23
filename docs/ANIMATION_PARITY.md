# Animation coverage by edition

Full's existing restoration at `ef5bfb66` was retained, not recreated. The fixed
upstream is v4.4.0 / `59c8bda3d1078155564267fbcb34fff9d2d80aff`.

| Contract | Full Animation Lite | Ultra Lite |
|---|---:|---:|
| Valid clips | 106 | 3 |
| Logical frames | 25,423 | 723 |
| Frame rate | 24 fps | 24 fps |
| Categories | 89 random, 6 events, 5 click, 3 move, idle, drag, turn | idle, click, drag |
| Supported logical canvas | 461 × 259 | 201 × 248 |
| Character scale | 72% of source | Original Lite 72% crop |
| Stored-pixel verification | Every frame equals the pinned official frame after the existing Lanczos resize and alpha crop | Every encoded frame equals historical commit 863353c5 |

The 106 count comes from the actual fixed official frame pack, not a rounded
README claim. No source frame was removed and no frame rate was reduced.
The pixels are not claimed to equal the original 640 × 360 source at full size:
the documented 72% conversion was inherited from the previous local restoration.
Arbitrary enlargement is not offered. High-DPI quality above the tested 100%
desktop remains unverified.

## Runtime reachability and timing

Each clip appears in the categorized animation menu. Click chooses among all five
Full reactions (one in Ultra); drag loops while held and returns to idle on release.
Full's scheduler uses the fixed upstream category weights and its calibrated
per-frame move curves. Turns complete before a direction reversal. A bounded
single stride is used per move; pointer interaction cancels it. Events remain
available through the menu without restoring AI, audio or network services.

Full does not reproduce the upstream's thrown-pet physics, arbitrary multi-loop
movement planning, service-triggered events or crossfade effects. Complete clip
availability is established; exact equivalence to every upstream interaction is
not claimed. Ultra has no roaming controller or Full-exclusive resources.

## Reproduction and evidence

`python lite/audit_animation.py` performs the full stored-pixel comparison using
locally held licensed source frames and historical Ultra Git objects. It does
not fetch character assets. The public code-only checkout lacks those inputs.

- [Full clip-by-clip results](../benchmarks/public/full-animation-manifest.json)
- [Ultra clip-by-clip results](../benchmarks/public/ultra-animation-manifest.json)
- [Edition totals and hashes](../benchmarks/public/animation-parity.json)

These checks establish stored content, sequence lengths and logical durations.
Qt paint timestamps are a separate diagnostic; neither proves physical monitor
Present cadence. Pointer, lifecycle and long-run acceptance are recorded separately.

The final full-frame audit also re-hashes every official input sequence against
the pinned per-clip source digest and verifies that each stored crop exactly equals
the complete nonzero-alpha bounding box. This checks that accessories/effects were
not omitted outside an otherwise pixel-correct cropped rectangle.
