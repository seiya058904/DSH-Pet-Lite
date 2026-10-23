# v1.0.1 package representation

Source and logical scope remain Core 11 / 2,651 and Ultra 3 / 723 at 24 fps.
Core packages 2,531 unique physical frames, Ultra 686. `frame_indices` maps each
logical frame to an exact-byte duplicate in the same clip; logical offsets are
never aliased. All Qt RGBA and premultiplied pixels are compared in both edition
test profiles. No re-encoding, resizing, alpha change or skipped timeline step.

# Core animation parity

Official fixed core: 11 clips / 2,651 frames, all 24 fps. Every frame was compared
against the publisher-hash-verified core ZIP after the inherited 461x259 Lanczos
normalization and complete nonzero-alpha crop. RGBA pixels, dimensions, offsets,
sequence digest and count passed. Ultra retains its established 723 encoded frames.

| ID | Name | Category | Frames | Reachability |
|---|---|---|---:|---|
| action_000 | 点击回应-傲娇生气 | click | 241 | menu plus click interaction/scheduling |
| action_001 | 点击回应-元气挥手 | click | 241 | menu plus click interaction/scheduling |
| action_002 | 点击回应-害羞惊讶 | click | 241 | menu plus click interaction/scheduling |
| click | 点击回应-开心跃动 | click | 241 | menu plus click interaction/scheduling |
| action_004 | 点击回应-挠痒咯咯笑 | click | 241 | menu plus click interaction/scheduling |
| drag | 被鼠标拖拽悬空反馈 | drag | 241 | menu plus drag interaction/scheduling |
| idle | 待机呼吸休闲 | idle | 241 | menu plus idle interaction/scheduling |
| action_013 | 左转奔跑 | move | 241 | menu plus move interaction/scheduling |
| action_014 | 漂浮踏步 | move | 241 | menu plus move interaction/scheduling |
| action_015 | 螃蟹走路 | move | 241 | menu plus move interaction/scheduling |
| action_105 | 东张西望 | turn | 241 | menu plus turn interaction/scheduling |

[Machine-readable audit](../benchmarks/public/core-animation-manifest.json).
The menu lists all 11 clips. Turns complete before direction reversal; pointer
interaction cancels movement. Core never selects a removed random/event clip.
The original program supports 106 clips, but the audited 348.97 MB base ZIP embeds
only these 11. Historical Full coverage is not current Core coverage.
