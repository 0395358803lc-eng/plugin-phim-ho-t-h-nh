# Video-hoạt-hình v1.11.0 — Macro approval orchestration

- 8 macro M0–M7 cover P00–P21; P00–P05 are authenticated prerequisites, P06 is the first technical stage.
- 99 packet template IDs retained; technical QC only. Normal packets inherit scope-based macro approvals; special actions remain separate.
- M0 P06; M1 P07–P09; M2 P10–P11; M3 P12–P13; M4 P14–P16; M5 P17–P18; M6 P19–P20; M7 P21.
- Canonical ordering: P06.12 before P06.09/10; P10.06 before storyboard; P14.06 before preview/QC; P17.07 before timeline QC/lock.
- Decision gates P08 profile, P10 visual before assets, P12 voice preset, P13 audio listening; P21 final user acceptance retained.
- OpenFilm CLI-first and VieNeu GPU CUDA first preserved. No network, model downloads, installer or Windows commands were run to prepare this plugin update.
- A skills-only plugin cannot start background chat turns; `Resume approved macro` is one new user-triggered turn after validating scope/revision and hashes.
- Validated with `python -m pytest -q` and ZIP integrity; no actual Windows end-to-end render acceptance in this release.
