# Third-party GTK / icon themes for Fedora 44 (GNOME 50.2, GTK 4.22)

Research date: 2026-07-19. Excludes all `vinceliuice` projects by request.
Every row cites a primary source. Claims I could not verify are marked **UNVERIFIED**.

## Method / evidence sources

- GitHub REST API (`api.github.com/repos/...`) for stars, git repo size, license, `pushed_at`,
  release tags/dates and verbatim release-note bodies.
- `dnf repoquery` on this Fedora 44 host for Fedora packaging (primary, not inferred).
- COPR project search API for third-party RPM presence.
- `src.fedoraproject.org` search and `gnome-look.org` product pages are **not usable** as
  evidence here: the former is behind an Anubis challenge, the latter renders download/rating
  counters via JS. Any gnome-look download number below would be fabricated, so none is given.

## Baseline: the libadwaita problem

Since GNOME 42, libadwaita applications do not read `gtk-theme-name` / `$GTK_THEME`. The only
mechanisms third-party themes use are:

1. **Drop a stylesheet at `~/.config/gtk-4.0/gtk.css`** (usually a symlink created by an
   `install.sh -l/--libadwaita` flag). libadwaita still loads user CSS from that path, so this
   partially restyles Adwaita apps. It is a recolor, not a real theme — widget geometry stays
   libadwaita's.
2. **Do nothing** — theme only GTK3/GNOME Shell and leave libadwaita alone (adw-gtk3's stance).
3. **Patched libadwaita** (`libadwaita-without-adwaita`) — out of scope, not shipped by any
   theme below and not in Fedora.

**UNVERIFIED:** I did not empirically confirm on this GNOME 50.2 / GTK 4.22 host that
`~/.config/gtk-4.0/gtk.css` is still honoured by libadwaita 1.8+. No upstream release note found
in this research says GNOME 50 broke it, but no source affirms it either. Worth a local test
before packaging anything that depends on mechanism (1).

---

## Ranked: GTK / GNOME Shell themes

| # | Theme | Repo | License | Latest release / commit | GNOME 50 / GTK 4.20+ evidence | Popularity | Ships | Packaging shape | Fedora / COPR |
|---|-------|------|---------|------------------------|-------------------------------|-----------|-------|-----------------|---------------|
| 1 | **adw-gtk3** | github.com/lassekongo83/adw-gtk3 | LGPL-2.1 | **v6.5, 2026-04-13**; pushed 2026-05-07 | **Strongest available.** v6.5 release body verbatim: *"Release for GNOME 50."* v6.4 body: *"**The GTK4 theme now requires GTK 4.20 or later.** The GTK4 theme now makes use of CSS `@media` query to apply the dark theme, therefore the version requirement bump."* | 2,024 stars | GTK3 port of libadwaita + a GTK4 companion stylesheet. No GNOME Shell theme, no icons. | **Meson** (2.3% of tree; SCSS 97.1%). ~8.9 MiB git checkout. | **Fedora ships `adw-gtk3-theme` 6.4-3.fc44** — i.e. one release *behind* the GNOME 50 release. COPR `nickavem/adw-gtk3`. |
| 2 | **Nordic** | github.com/EliverLara/Nordic | GPL-3.0 | Last tag v2.2.0 (2022-06-24) — stale; **commits 2026-05-04** | **Explicit, commit-level.** Two commits dated 2026-05-04: *"fix(gtk): fix styling issues with nautilus pathbar in gnome v50"* and *"fix(gtk): fix alignment issues with nautilus sidebar in gnome v50"*. | 2,706 stars | GTK2/3/4, GNOME Shell, KDE, Cinnamon, Metacity, XFWM4 | Copy-to-`~/.themes` tarball; no install.sh variant matrix. ~18.1 MiB git. | None found in Fedora repos (`dnf repoquery` returned nothing). |
| 3 | **GNOME-macOS-Tahoe** | github.com/kayozxo/GNOME-macOS-Tahoe | **None declared** | **v0.6.3, 2026-07-07** | **Weak/indirect.** README documents libadwaita handling from GNOME 43 onward but names no GNOME 49/50 version. Recency (July 2026) is the only signal. | 1,063 stars | GTK3 + GTK4, GNOME Shell, MacTahoe icons, GDM, cursors, wallpapers | Interactive `install.sh`, plus flags (`--color` × 16 accents, `-la` for libadwaita) | None found. |
| 4 | **Celestial** | github.com/zquestz/celestial-gtk-theme | GPL-3.0 | **v1.3.5, 2026-07-16** | **Negative evidence.** README states support for **"GNOME Shell 38-48"** — explicitly stops at 48. Actively developed but not documented for 50. | 26 stars | GTK2/3/4, Shell, Xfce, Cinnamon, Budgie, GDM, cursors, Kvantum; 12 variants | `./install.sh` → `~/.themes`. ~69.7 MiB git (large: bundles wallpapers). | None found. |
| 5 | **Gruvbox-GTK-Theme** | github.com/Fausto-Korpsvart/Gruvbox-GTK-Theme | GPL-3.0 | **Last commit 2025-10-23** (~9 months stale) | **None.** No GNOME 48/49/50 statement in README or commits. Last commit predates GNOME 50 (March 2026) entirely, so its Shell CSS cannot cover GNOME 50 nodes. | 988 stars | GTK3 + GTK4, GNOME Shell, icons; Cinnamon/XFCE/Mate | `install.sh` with `-t` (9 accents), `-c` light/dark, **`-l/--libadwaita`**, `--tweaks` (medium/soft/black/float/outline). Needs `sassc`, `murrine-engine`, `gnome-themes-extra`. ~40.6 MiB git. | None found. |

Sibling of #5: `Fausto-Korpsvart/Material-GTK-Themes`, same author, same install.sh design, same
last-commit date 2025-10-23, only 146 stars. Same GNOME 50 gap. Not ranked separately.

### Reading of the GTK table

Only **adw-gtk3** and **Nordic** have GNOME-50-specific evidence, and they are complementary:
adw-gtk3 is the GTK3/GTK4 stylesheet with no Shell theme; Nordic has a Shell theme with
commit-level GNOME 50 fixes but a 4-year-old release tag. Ranks 3-5 are recency/popularity
picks with no GNOME 50 claim, and #4 carries an explicit "up to 48" statement.

**adw-gtk3 is the single clearest packaging opportunity**: Fedora is at 6.4 while upstream 6.5
is the GNOME 50 release, and 6.4 is exactly the release that raised the floor to GTK 4.20 —
Fedora 44 ships GTK 4.22, so both are installable, but F44 users get the pre-GNOME-50 stylesheet.

---

## Ranked: icon themes

| # | Theme | Repo | License | Latest release / commit | GNOME 50 evidence | Popularity | Ships | Packaging shape | Fedora / COPR |
|---|-------|------|---------|------------------------|-------------------|-----------|-------|-----------------|---------------|
| 1 | **MoreWaita** | github.com/somepaulo/MoreWaita | GPL-3.0 | Tag **v49 (2025-12-11)**; **commits to 2026-06-23** | **Indirect but systematic.** Version numbers track GNOME releases (v48.3.1, v48.4, v49). v49 notes: *"3 years in development and the milestone of 500 supported apps."* **No v50 tag yet** and no release note names GNOME 50. | 1,055 stars | Adwaita *companion* — scalable app icons, symbolics, MIME types. Explicitly "adds to Adwaita, does not modify it". | **Both `install.sh` and `meson.build`**; has a `PACKAGING.md`. ~13.5 MiB git — smallest good candidate. | None found in Fedora repos. |
| 2 | **Papirus** | github.com/PapirusDevelopmentTeam/papirus-icon-theme | GPL-3.0 | Tag **20250501**; **commits to 2026-06-28** | **None GNOME-specific.** Recent releases are Plasma-6-oriented. Desktop-agnostic by design. Release cadence has slowed — no tag in 14 months despite active commits. | **7,931 stars** — by far the most popular | Papirus / -Dark / -Light, thousands of app+MIME icons, hardcode-tray, folder-color, KDE colorscheme | Install script + wide distro packaging. **~347 MiB git** — the largest by an order of magnitude. | **Already in Fedora**: `papirus-icon-theme`, `-dark`, `-light` all 20250501-2.fc44. Repackaging adds nothing. |
| 3 | **Kora** | github.com/bikass/kora | GPL-3.0 | **v2.0.4, 2026-04-14** (v2.0.3 2026-04-10, v2.0.2 2026-04-07); pushed 2026-05-05 | **None.** No GNOME version statement. Strong *cadence* evidence: 75 releases, three in one month of 2026. | 919 stars | kora (blue folders) + kora-pgrey (grey folders), SVG | Copy to `/usr/share/icons` or `~/.local/share/icons`; README claims existing Arch/**Fedora**/openSUSE/Solus packages. ~57.6 MiB git. | **Not present in Fedora repos** on this host — `dnf repoquery 'kora-icon-theme*'` returned nothing. The README's "Fedora" claim is **UNVERIFIED** and likely refers to a COPR. |
| 4 | **Adwaita-colors** | github.com/dpejoh/Adwaita-colors | GPL-3.0 | **v2.6, 2026-05-18**; pushed 2026-06-07 | **Partial.** README states **GNOME 47+** required (accent-color feature). Ties into GNOME's own accent API, so it tracks GNOME rather than fighting it. No explicit 50. | 258 stars | Recolors the Adwaita icon theme to match the system accent; optional "Adwaita Colors Home" Shell extension | Interactive `./setup` script, sudo or `~/.local/share/icons`. Needs `adwaita-icon-theme` + `gtk-update-icon-cache`. **~5.1 MiB git — smallest of all candidates.** | None found. |
| 5 | **Reversal** | github.com/yeyushengfan258/Reversal-icon-theme | GPL-3.0 | **Last commit 2026-03-17** (icon additions only) | **None.** No GNOME version statement anywhere. Before the 2026-03-17 PR merges, the prior commit was 2025-11-14 — maintenance is drive-by icon PRs, not upkeep. | 701 stars | Colorful rectangle icon set, 13 color variants | `install.sh` with `-d` dest, `-n` name, `-t` (13 colors + `all`), `-a` alternative macOS-style, `-b` bold panel, `-r` remove. 100% Shell. ~15.4 MiB git. | None found. |

Notable near-misses: **Nordzy-icon** (417 stars, GPL-3.0, last commit 2026-04-27 — two icon
additions), **Delta-Icons/linux** (102 stars, **CC-BY-NC-ND-4.0 — non-commercial + no-derivatives,
not Fedora-acceptable**), **Sevi** (108 stars, CC-BY-SA-4.0, pushed 2026-07-17, a Reversal
derivative), **Suru++** (389 stars).

### Reading of the icon table

Icon themes are largely GNOME-version-agnostic — they are SVG + `index.theme`, with no CSS that
GNOME 50 could break. So "GNOME 50 evidence" is weak across the board *and that is fine*; the
real quality signal is icon-coverage cadence. On that basis MoreWaita (commits within a month,
ships `meson.build` and a `PACKAGING.md`, small tree, not in Fedora) is the best packaging target.

---

## Candidates rejected, with reason

| Candidate | Reason |
|-----------|--------|
| Colloid, Fluent, Orchis, Qogir, WhiteSur, Tela, **Graphite**, MacTahoe, Fluent-icon, WhiteSur-icon | All `vinceliuice`. Note **Graphite** surfaces in most "best theme" search results but is vinceliuice — excluded. |
| **catppuccin/gtk** | **Archived 2024-06-02**, read-only. Last release v1.0.3 (2024-06-01). Maintainers' stated reason: GTK theming is *"a nightmare to consistently theme and maintain."* Dead. |
| **Marble-shell-theme** | 547 stars, good Python installer, but README states *"GNOME 42-48. Correct functionality on other versions is not guaranteed."* Last release 48.3.2 (2025-07-07), last push 2025-07-24 — a full year stale, spans both GNOME 49 and 50. |
| **Material-GTK-Themes** (Fausto-Korpsvart) | Strictly dominated by the same author's Gruvbox theme: identical install.sh design and identical 2025-10-23 last commit, but 146 vs 988 stars. |
| **Papirus** (as a packaging target) | Already in Fedora at the current upstream tag (20250501-2.fc44). Ranked #2 on merit; rejected as *work to do*. |
| **Yaru** | Already in Fedora (`yaru-gtk3-theme`, `yaru-gtk4-theme`, `yaru-icon-theme`, etc. at 25.10.3-3.fc44). Also Ubuntu-default, not really "third-party alternative". |
| **Numix** | In Fedora, but `numix-icon-theme` is at 24.04.22 and `numix-gtk-theme` at 2.6.7-18 — upstream is effectively dormant. |
| **Delta-Icons/linux** | License is **CC-BY-NC-ND-4.0**. Non-commercial and no-derivatives clauses make it non-free; unpackageable for Fedora/COPR. |
| **GNOME-macOS-Tahoe** (caveat, not rejection) | **Declares no license** in repo metadata (GitHub API `license: null`). Ranked #3 on activity, but unlicensed = unpackageable until upstream clarifies. Also a 228 MiB git tree. |
| **Darkwaita** | Genuinely says *"Gnome 48/49/50"* and is MIT — the cleanest GNOME 50 claim found. Rejected from the table because it is trivial in scope: 35 stars, 5 total commits, ships one patched `gnome-shell.css` with darkened greys. Not a theme worth an RPM, but worth knowing about. |
| **themix-gui**, **pywal16-libadwaita**, **adwaita-material-you** | Theme *generators*, not themes. Different packaging problem. |
| **firefox-gnome-theme**, **discord-gnome-theme** | Application chrome, not GTK/Shell themes. |

---

## Claims I could NOT verify

1. **gnome-look.org download counts and ratings for any theme** — pages are JS-rendered; WebFetch
   returns only the HTML shell. No download figure appears anywhere above.
2. **Whether `~/.config/gtk-4.0/gtk.css` still restyles libadwaita apps on GNOME 50.2 /
   libadwaita 1.8** — the `-l/--libadwaita` mechanism used by Gruvbox, Material, and
   GNOME-macOS-Tahoe rests on it. Test locally before relying on it.
3. **Kora's claimed Fedora package** — README asserts Fedora packaging; `dnf repoquery` on this
   F44 host finds none. Probably a COPR, unconfirmed.
4. **COPR coverage generally** — the COPR web search is behind an Access-Denied wall; only the
   `api_3/project/search` endpoint worked, and it matches project names/descriptions, not built
   package names. A theme could exist inside a large personal COPR (e.g. `mzink/Utils`,
   *"Various RPM's for my desktop. GTK theme, icon themes and other utilities."*) without
   surfacing. Absence of a COPR hit above is not proof of absence.
5. **src.fedoraproject.org dist-git state** — unreachable (Anubis). All Fedora packaging claims
   above come from `dnf repoquery` against the enabled F44 repos on this host, which reflects
   *shipped* packages, not retired or in-review ones.
6. **Tarball sizes** — the MiB figures are GitHub's `size` field (git repo size, in KiB), not
   release-tarball sizes. They are an upper bound and include full history where GitHub counts it.
7. **MoreWaita GNOME 50 support** — inferred from its GNOME-tracking version scheme plus June 2026
   commits. There is no v50 tag and no release note naming GNOME 50.
