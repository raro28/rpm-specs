# CLAUDE.md

RPM spec files for Fedora 44, built in the raro28/wdm COPR. One subdirectory per
source package. See README.md for per-spec build details.

## Verify, don't assert (governing rule)
- State only analytically verified facts. Back every claim with evidence — a
  command's output, a file's contents, an engine/build result — never memory,
  assumption, or "should work."
- "Verified" means reproduced on this host: build it (`mock` exit 0), parse it
  (real GTK engine), diff it against ground truth (`gresource extract`), grep the
  actual compiled output. A plan is not a result.
- Derive from the reference implementation present on this host (GNOME 50.2,
  GTK 4.22) — not from training data or upstream READMEs.
- When something is unverified or unverifiable (e.g. live pixel rendering), say so
  explicitly; never imply it was checked.
- No silent scope: report what you ran, what passed, and what you skipped.
- Prefer upstream/fork fixes you can verify over hand-authored guesses; if you
  must author a fix, prove it with the engine/build before claiming it works.

## Style: terse and factual
- Write factually, no filler — in prose, spec files, `%changelog` entries, and
  comments alike. No marketing, no hedging, no restating the obvious.
- Keep edits minimal; match the surrounding file's brevity and idiom. State what
  changed and why in as few words as the fact needs.

## Build / verify loop
- Target = Fedora 44 (GNOME 50.2, GTK 4.22); build in a clean chroot.
- Flow: `spectool -g -R <spec>` → `rpmbuild -bs <spec>` →
  `mock -r fedora-44-x86_64 <srpm>`. Output in `/var/lib/mock/fedora-44-x86_64/result/`.
- mock reads `~/rpmbuild/SOURCES/` (the `spectool` step populates URL sources); stage
  local patches there first (`cp <dir>/*.patch ~/rpmbuild/SOURCES/`).
- Lint gate: `rpmlint -c rpmlint.toml */*.spec` must report `0 errors, 0 warnings`
  before work is done.

## Spec conventions
- Downstream patch / packaging change → bump `Release`, keep upstream `Version`.
  Change `Version` only when the upstream source changes.
- Use `%autosetup -p1` (not `%setup`) when `PatchN:` is present.
- `%changelog`: escape macros as `%%` (e.g. `%%autosetup`); entry header
  `* Day Mon DD YYYY Name <email> - VERSION-RELEASE`.
- Patch files live in the spec's subdirectory, named by purpose.

## Keep README.md in sync
When a spec changes, update README.md in the same change, then re-check the lint
gate. Spots that drift:
- Specs table — `Version-Release` and "what it ships".
- The per-spec build section — staged sources and the `<srpm>` filename.
- Quick-reference table — local/URL sources.
- Linting section — `%check`/filter counts.

## vinceliuice GTK themes (colloid/fluent/orchis/qogir/whitesur)
- install.sh clamps GNOME shells ≥48 to the 48-era stylesheet
  (`shell-48-0`/`widgets-48-0`), leaving GNOME 50 nodes unstyled; downstream
  patches add coverage (README → "vinceliuice GTK themes").
- Each carries a `%check` (`BuildRequires: gtk4 python3-gobject-base`): parses
  compiled `gtk-4.0` CSS via `GtkCssProvider` (headless in mock) and greps the
  GNOME 50 selectors in `gnome-shell.css`.
- GNOME 50 ground truth (from this host): shell nodes from
  `/usr/share/gnome-shell/gnome-shell-theme.gresource`; libadwaita CSS from
  `/usr/lib64/libadwaita-1.so.0` (both via `gresource extract`).

## Environment
- An `rtk` hook rewrites shell commands. Generate patches with `rtk proxy git diff`
  — plain filtered output is not a valid applyable diff.

## Git
- Default working branch: `develop` (PRs target `main`). Commit/push only when asked.
