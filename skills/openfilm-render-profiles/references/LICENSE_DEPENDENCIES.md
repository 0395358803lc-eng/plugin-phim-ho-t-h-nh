# N17 — Dependency inventory / licensing checklist

**Do not install packages at audit time (P04).** Only identify packages with existing package.json, package-lock.json/pnpm-lock.yaml, module paths and actual version metadata. Check each item in P05.

| ID | Only when | Package(s) | Verification |
|---|---|---|---|
| B05 | Remotion Master | `react`, `react-dom` | installed versions + React/Remotion compatibility |
| B06 | Remotion 3D | `@react-three/fiber` | resolves under actual project; compatible `three` |
| B07 | Remotion 3D | `@remotion/three` | same Remotion generation and correct API |
| B08 | Remotion Master | `@remotion/renderer`, `@remotion/cli` | renderer and Chromium deps present; CLI name and flags from `--help` after approval |
| B09 | TypeScript + Three | `@types/three` | matching version, can be not needed without TS |
| B10 | TSX project | `typescript` + tsconfig | build resolution and project-specific configs |

The attached research report's 19/11/2026 version snapshot (GSAP 3.15.1 / Three 0.187.0 / Remotion 4.0.545) is a *reference*, not an order to upgrade existing compatible versions. When patching, pin through a lockfile; source hashes, provenance, package and model licenses must be checked independently.

**License gates:** OpenFilm project MIT, Three.js MIT, VieNeu-TTS code Apache-2.0 (model weights separate), GSAP terms as published for the actual use case, Remotion licensing by organization and activity; fonts/music/SFX/GLB individually licensed. Never presume all are MIT. Voice cloning only with appropriate authorization, protect reference audio.
