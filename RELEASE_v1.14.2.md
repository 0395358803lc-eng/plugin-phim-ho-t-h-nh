# Release v1.14.2

**Goal:** Storyboard as data only, code-first assets, equal OpenFilm CLI/Remotion engine selection.

P10 outputs storyboard.json + STORYBOARD.md, no generated pictures; P11 no mandatory raster/ZIP. Remotion Master bypasses OpenFilm CLI-only dependencies; OpenFilm Master continues CLI. No changes to number of macro groups or existing 99 template IDs.

Compatibility: legacy packet definitions retain IDs; branch-specific packets must be skipped for the inactive engine and replaced with engine-equivalent outputs, not faked. Real host and Windows render integration remain to be tested.
