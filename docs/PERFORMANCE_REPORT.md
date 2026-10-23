# Performance report

**Status: local dual-edition validation; public dual binary release blocked.**
See [methodology](BENCHMARK_METHODOLOGY.md) before comparing these products.

| Metric | Official full no-chat A | Previous three-action Lite B | Full C | Ultra D |
|---|---:|---:|---:|---:|
| Animation clips | 106 | 3 | 106 | 3 |
| ZIP, decimal MB | 348.97, historical | 55.60, historical | 1,034.44 | 55.62 |
| Expanded, decimal MB | 576.93, historical | 98.60, historical | 1,074.00 | 98.61 |
| Historical Private Bytes mean, MB | 80.03 | 55.47 | Not comparable to historical sample | Not yet independently compared |
| Historical Working Set mean, MB | 121.54 | 82.65 | Not comparable to historical sample | Not yet independently compared |
| Validated CPU percentage | Not reliable | Not reliable | Not reliable | Not reliable |
| GPU / watts / physical Present | Not measured | Not measured | Not measured | Not measured |

## Full Animation Lite — Benchmarks

The locally built Full ZIP is 1,034,437,183 bytes and the expanded package is
1,073,996,800 bytes. Every promised animation is included. Its frame-based lossless
storage is larger than the official WebM distribution; no size reduction is claimed.
The bounded idle cache holds roughly 29.28 MB of decoded pixel data; other action
frames are transient. It imports no multimedia decoder, network stack or upstream
application graph. The final installed-binary soak is in progress at this report revision.

## Ultra Lite — Benchmarks

The locally built Ultra ZIP is 55,620,173 bytes and the expanded package is
98,606,631 bytes. This is essentially the historical package footprint, with new
edition identity and safety behavior. Its 723 encoded frames are identical to the
historical baseline. Full-exclusive clips, stride data and roaming module are absent.
The final installed-binary soak is in progress at this report revision.

## Trade-offs & What to Choose

Choose Full for all restored animation clips and local roaming. Choose Ultra for
the smallest existing core-animation package. Keeping original 24 fps timing and
input behavior takes priority over a lower resource number. No CPU, power or GPU
percentage improvement is asserted from cycle counters or incomparable historical runs.

## Experiments and limits

The [retained probes](../benchmarks/public/optimization-probes.json) compare stronger
lossless encoding, a stored resource container, and smaller/no idle caches. Encoding
saves about 3%; the container yields a small absolute decode-time difference; reduced
caching increases repeated decode work substantially. None was adopted. This supports
stopping these specific experiments, not a claim of a globally optimal implementation.

Real 100% desktop pointer tests passed separately for both final executables, including
actual menu Exit and relaunch. Earlier failed probes and the interrupted pre-fix soak
remain local evidence. A focus-sensitive click attempt also failed before the test
explicitly activated its own pet window. Physical tray-icon input, higher DPI, multiple
screens, offline network disconnection, GPU/watts and monitor Present remain unverified.

The OSV exact-version query returned no advisory records for the seven queried packages;
that is limited database evidence, not proof of absence of vulnerabilities.
[Query record](../benchmarks/public/dependency-audit.json).
