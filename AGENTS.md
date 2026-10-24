# DSH Pet Lite Core/Ultra

No subagents. Remote changes require explicit user authorization.
Preserve user changes and prior release history. Read ASSET_LICENSE.md and docs/BUILD.md.
Only Core 11 / Ultra 3 assets belong to the current release; no Full/extra packs.
Run both DSH_TEST_EDITION profiles, ruff, real-asset builds/closure/CRC and diff checks.
Real GUI/tray input and soak validation are separate from offscreen CI.
No network runtime, hidden polling, services, autostart or global system changes.
Do not publish private logs, settings, credentials or personal paths.

## 已知问题处理决定

- 2026-10-24 审计 A07：已知 Core 在两侧可用空间均不足移动步幅时可能反复转身，现有证据为 Qt offscreen 窄逻辑工作区且 Ultra 不受此路径影响；本轮决定暂不修，实际使用遇到后再经用户授权处理。
