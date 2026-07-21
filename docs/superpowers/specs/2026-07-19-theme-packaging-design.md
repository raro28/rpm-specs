# Theme/icon packaging: variants, naming, repo layout

Date: 2026-07-19. Target: Fedora 44 (GNOME 50.2, GTK 4.22), COPR `raro28/wdm`.

Covers three coupled changes to the 9 vinceliuice theme/icon specs: ship variant
subpackages, standardize package names, and group the repo by category. Plus a
survey of non-vinceliuice alternatives (appendix).

## Evidence base

Every count below comes from a real install run on this host, not from reading
usage text. That distinction mattered twice: the usage text omits an entire axis
(section 1.2), and it describes `default` without revealing it is an alias for
blue (section 1.4).

- Repo contents: `find -name '*.spec'` — **14** spec directories, of which **9**
  are vinceliuice theme/icon specs (`grep -l vinceliuice */*.spec`).
- Variant counts: `./install.sh` executed per project into a scratch dest with
  `HOME` redirected, output directories counted.
- Fedora naming: `dnf repoquery` over the `fedora` repo — 67,430 package names.
- Sizes: `tar | zstd -19` (RPM's default payload codec).

**Methodology note.** An `rtk` hook on this host intercepts `grep` and rewrites
its output, which silently corrupts `$(grep ...)` command substitution. All
grep-derived facts below were re-verified through `rtk proxy grep`. Also note
this shell is zsh: unquoted parameter expansion does **not** word-split, so
argument lists built in variables must use `${=var}` or be passed literally.

## 1. Variant matrices

### 1.1 The flags are not consistent across the author's own projects

| Flag | Colloid / Fluent / Orchis / WhiteSur-gtk | Qogir | Tela / Tela-circle |
|---|---|---|---|
| `-c` | color (`standard\|light\|dark`) | color | **no argument** — "circular"/"plasma folder" |
| `-t` | accent color (9) | *primary* color (3) | **does not exist** |
| color selection | `-c` / `-t` | `-c` / `-t` | **positional argument** |

Verified in `Tela-circle-icon-theme/install.sh:273-302`: `-c` sets
`circle="true"` and performs **no `shift`** (lines 276-278), so the following
token falls through to the color-variant branch (line 289). Therefore
`tela-circle-icon-theme.spec`'s `./install.sh -d <dest> -c standard` means
*circular folder version* **plus** positional color `standard` — not
"color=standard" as the other specs' identical-looking `-c` implies.

### 1.2 The hidden DPI axis, and why it is dropped

Four of the five GTK themes emit `-hdpi` / `-xhdpi` directories automatically.
The axis appears in no `usage()` output. It is also **useless on GNOME**:

Building Orchis and comparing top-level contents:

```
Orchis/       cinnamon COPYING gnome-shell gtk-2.0 gtk-3.0 gtk-4.0
              index.theme metacity-1 plank xfwm4
Orchis-hdpi/  xfwm4
```

`Orchis-hdpi` has no `gtk-3.0`, no `gtk-4.0`, no `gnome-shell`, and no
`index.theme` — it is not a valid standalone theme, only an XFCE
window-decoration asset set. Corroborated in source: Colloid's hdpi output is
`xfwm4/themerc` with `button_offset` 6 -> 9 -> 12
(`Colloid/install.sh:158-163`); WhiteSur's is `assets/xfwm4/*.png`
(`WhiteSur/libs/lib-install.sh:501,505`).

Independently, this host needs no HiDPI at all: `scaling-factor=0` (auto),
`text-scaling-factor=1.0`, no fractional-scaling experimental features; a 2560x1440
primary and 1920x1080 secondary both run at scale 1.

**Dropped.** GTK4 handles scaling natively, so this stays correct even on a
future 4K panel.

### 1.3 Full matrices, for context only

`./install.sh -t all`, all other axes at defaults — the unconstrained sets:

| Project | Directories | Decomposition |
|---|---|---|
| qogir-icon-theme | 9 | 3 theme x 3 color |
| whitesur-icon-theme | 27 | 9 theme x 3 color |
| tela-icon-theme | 45 | 15 color x 3 bright |
| tela-circle-icon-theme | 45 | 15 color x 3 bright |
| qogir-theme | 15 | asymmetric (below) |
| fluent-gtk-theme | 54 | 9 accent x 3 color x 2 size |
| colloid-gtk-theme | 81 | 9 accent x 3 color x 3 DPI |
| whitesur-gtk-theme | 108 | 9 accent x 2 color x 3 DPI x 2 opacity |
| orchis-theme | 162 | 9 accent x 3 color x 2 size x 3 DPI |
| **total** | **546** | **-> 200 subpackages** |

Qogir's asymmetry, from its full listing: the `default` theme gets DPI variants
(9 dirs = 3 color x 3 DPI) while `Manjaro` and `Ubuntu` get 3 each with no DPI.
9 + 3 + 3 = 15.

Unrestricted matrices — every documented tweak, logo and radius combined — were
**not** enumerated; order of magnitude runs ~10^3 (Qogir) to ~10^5 (Orchis, with
13 radii and 7 shell versions). Whether tweak flags are mutually exclusive was
not tested, so no exact product is claimed. The branded-logo axis (14-21 values,
Orchis being 21) styles one Activities button and is dropped.

### 1.4 Color vocabulary: the common set is one color

| Project | Accent colors offered |
|---|---|
| Colloid / Fluent / Orchis | default, purple, pink, red, orange, yellow, green, **teal**, grey |
| WhiteSur-gtk | default, **blue**, purple, pink, red, orange, yellow, green, grey |
| WhiteSur-icon | default, purple, pink, red, orange, yellow, green, grey, nord |
| Tela / Tela-circle | standard, **black**, **blue**, brown, green, grey, orange, pink, purple, red, yellow, manjaro, ubuntu, dracula, nord |
| **Qogir-theme / Qogir-icon** | **default, Manjaro, Ubuntu — no accent colors at all** |

Both Qogir packages expose distro branding rather than accents, which caps the
universal intersection at a single color. Excluding them, the other 7 share
green, grey, orange, pink, purple, red, yellow.

`default` **is** blue, verified in source rather than usage text: Colloid's
`src/sass/_color-palette-*.scss` define `$default-light: $blue-light` and
`$default-dark: $blue-dark`. Colloid, Fluent and Orchis expose no `blue` token —
`default` is the only route to it. WhiteSur-gtk and Tela offer `blue` explicitly.

Availability of the candidate favourites: blue 9/9 (as `default` in five), red
7/9, grey 7/9, **teal 3/9** (Colloid/Fluent/Orchis only), **black 2/9** as a
colour (Tela only; Colloid and Orchis expose it via `--tweaks black`, a
different axis that restyles the whole theme).

**Decision.** Standardize on **blue + red + grey**. Teal and black are too rare
to name consistently across packages. Qogir ships its default only.

### 1.5 Measured constrained build

Actual runs with the decisions above applied:

| Project | Dirs | of which hdpi | Kept | Subpackages |
|---|---|---|---|---|
| colloid-gtk-theme (standard) | 27 | 18 | 9 | 3 |
| colloid-gtk-theme (compact) | 27 | 18 | 9 | 3 |
| fluent-gtk-theme | 18 | 0 | 18 | 6 |
| orchis-gtk-theme | 54 | 36 | 18 | 6 |
| qogir-gtk-theme | 9 | 6 | 3 | 1 |
| whitesur-gtk-theme | 36 | 24 | 12 | 6 |
| qogir-icon-theme | 3 | - | 3 | 1 |
| whitesur-icon-theme | 9 | - | 9 | 3 |
| tela-icon-theme | 9 | - | 9 | 3 |
| tela-circle-icon-theme | 9 | - | 9 | 3 |
| **total** | | | **99** | **35** |

**35 subpackages**, down from 200 — the colour constraint and the DPI drop each
account for roughly half the reduction.

## 2. Naming

Measured convention:

- **Icons: `<name>-icon-theme`.** 28 Fedora packages end in it. 14 more contain
  `icon-theme` and are variant or `-devel` subpackages of those 28 — which *is*
  the convention, not an exception. Only 4 names contain `icon-theme` without
  descending from a base: 3 are Rust crates (`rust-linicon*`, false positives)
  and 1 is `libreoffice-icon-theme-papirus`, an application's bundled copy.
- **GTK: no principled rule.** `-gtk3-theme` (5), `-gtk-theme` (4),
  `-gtk4-theme` (3), `-gtk2-theme` (3), bare `-theme` (arc-theme,
  sweet-gtk-theme). The suffix does not track content — the two bare/`gtk`
  examples differ in the *opposite* direction from what their names suggest:

  | | `gtk-2.0` | `gtk-3.0` | `gtk-4.0` | gnome-shell | cinnamon | unity |
  |---|---|---|---|---|---|---|
  | `arc-theme` (no `gtk` in name) | yes | yes | **yes** | yes | yes | no |
  | `deepin-gtk-theme` (`gtk` in name) | yes | yes | **no** | yes | yes | yes |

  The package *without* `gtk` in its name is the one shipping a GTK 4 theme.
  Historical accident; `-gtk-theme` is the plurality for single-package GTK
  themes.
- **Variants are subpackage suffixes on one source package**, never separate
  source packages: `numix-icon-theme-circle`, `numix-icon-theme-square`,
  `papirus-icon-theme-dark`, `papirus-icon-theme-light`.

That last point makes `fluent-gtk-theme-compact` the one true defect: a variant
promoted to a source-package name. Its directory also disagrees with its `Name:`.

| Now | After | Reason |
|---|---|---|
| `fluent-gtk-theme-compact` | `fluent-gtk-theme` | variant must not be a source-package name |
| `orchis-theme` | `orchis-gtk-theme` | minority suffix |
| `qogir-theme` | `qogir-gtk-theme` | minority suffix |
| `colloid-gtk-theme` | unchanged | compliant |
| `whitesur-gtk-theme` | unchanged | compliant |
| all four `*-icon-theme` | unchanged | compliant |

Clean break, no `Obsoletes`/`Provides`. Old COPR packages are removed with
`copr-cli delete-package wdm --name <old>`; locally installed old packages become
orphans the user removes manually.

## 3. Subpackage scheme

Group each accent's light/dark/standard triple into one subpackage — GNOME
switches between light and dark at runtime, so splitting them yields
subpackages that are useless alone. Size and opacity stay separate; they are
mutually exclusive user choices, not runtime-switched.

```
fluent-gtk-theme-grey          -> Fluent-round-grey, -grey-Light, -grey-Dark
fluent-gtk-theme-grey-compact  -> the same three, -compact
whitesur-gtk-theme-red-solid   -> WhiteSur-{Light,Dark}-solid-red
qogir-gtk-theme                -> Qogir, Qogir-Light, Qogir-Dark  (default only)
```

**35 binary subpackages from 9 source packages** (25 GTK + 10 icon), one build
each. The main package ships `COPYING` and docs only; every theme directory
lives in a subpackage.

Naming note: where upstream spells blue as `default`, the subpackage is still
named `-blue`, since the RPM name should describe the colour, not the upstream
flag. The spec records the flag mapping in a comment.

## 4. `-l/--libadwaita` is a packaging no-op (all five GTK themes, verified)

Two Fluent installs, identical flags except `-l`, produced **byte-identical**
trees (`diff -rq` clean). `-l`'s only effect is writing
`$HOME/.config/gtk-4.0/{gtk.css,gtk-dark.css,assets}` — outside `--dest`, so
nothing reaches the buildroot. The `gtk-4.0/` directory ships regardless as part
of each theme (405 such paths in the current `fluent-gtk-theme-compact` RPM).

So that spec's `%changelog` claim *"Add -l (libadwaita) to install.sh for
GTK4/libadwaita app theming"* is false in packaging terms: it adds no files and
writes to the builder's `$HOME` during `%install`.

Remove `-l` from `fluent-gtk-theme.spec`.

**Now verified for all five GTK themes.** Each was built twice, identical flags
except `-l`, and the trees diffed:

| Theme | `-l` (bare) | Note |
|---|---|---|
| fluent-gtk-theme | identical | |
| colloid-gtk-theme | identical | also `-l system`: identical |
| orchis-gtk-theme | identical | |
| qogir-gtk-theme | identical | |
| whitesur-gtk-theme | identical | also with the spec's full `-N mojave --shell -i gnome` set |

**One real exception:** `colloid -l fixed` **does** alter the buildroot — 6 files,
the `gtk-4.0/gtk.css` and `gtk-dark.css` of `Colloid`, `Colloid-Dark` and
`Colloid-Light` — because it bakes in a fixed accent instead of following the
system colour scheme. This does not affect the decision: every spec in this repo
passes `--libadwaita` **bare**, which is the `system` default and byte-identical
to omitting the flag. `-l fixed` is never used. If a future spec wants fixed
accents, `-l` stops being a no-op and must stay.

## 4.5 Stripping non-GNOME desktop payload

Each GTK theme variant ships components for desktops this COPR does not target.
Measured in one Orchis variant (1.6 MB apparent): `gtk-3.0` 588K, `gtk-4.0`
616K, `gnome-shell` 156K, `gtk-2.0` 105K, `cinnamon` 75K, `metacity-1` 32K,
`xfwm4` 30K, `plank` 2.7K.

**Removed** — `cinnamon`, `xfwm4`, `plank`, `unity`. None of these desktops is
installed on this host, and none has a GNOME code path. Compressed saving on the
constrained sets, measured:

| Project | full | stripped | saved |
|---|---|---|---|
| colloid-gtk-theme | 235 KB | 175 KB | 25% |
| orchis-gtk-theme | 467 KB | 342 KB | 26% |
| qogir-gtk-theme | 1122 KB | 962 KB | 14% |
| whitesur-gtk-theme | 430 KB | 257 KB | 40% |

**Kept, deliberately** — both are the "older applications" exception:

- `gtk-2.0`: `gtk2` is installed here and **246 packages in the F44 repos still
  link `libgtk-x11-2.0.so.0`**, so a GTK2 app remains installable at any time.
  105 KB per variant is cheap insurance. (Note the current installed dependents
  are all gtk2 infrastructure — `gtk2-engines`, `ibus-gtk2`, `libcanberra-gtk2`,
  `gtk-murrine-engine` — not applications.)
- `metacity-1`: `metacity` 3.58.1 and `gnome-flashback` 3.58.0 are both in the
  F44 repos. GNOME Flashback is a GNOME session that reads this directory. Not
  installed here, but it is a GNOME path, not a foreign-desktop one.

`adwaita-gtk2-theme` is **not** in the F44 repos — the copy installed here is an
fc43 leftover, confirming the note in `fluent-gtk-theme-compact`'s changelog.

Implemented as a `find -delete` in `%install`, with a `%check` gate asserting
zero `cinnamon`/`xfwm4`/`plank`/`unity` directories survive. Verified against the
shipped RPM: `rpm -qlp fluent-gtk-theme-blue` lists exactly `gnome-shell`,
`gtk-2.0`, `gtk-3.0`, `gtk-4.0`, `index.theme`, `metacity-1`.

Note the DPI drop (section 1.2) already removes the largest xfwm4 payload, since
`-hdpi`/`-xhdpi` directories are xfwm4-only.

## 5. Repo layout

```
themes/  colloid-gtk-theme fluent-gtk-theme orchis-gtk-theme
         qogir-gtk-theme whitesur-gtk-theme
icons/   qogir-icon-theme tela-icon-theme tela-circle-icon-theme
         whitesur-icon-theme
apps/    mural gnome-shell-extension-per-monitor-wallpaper
         looking-glass-client llama.cpp
kernel/  looking-glass-kvmfr-kmod
docs/    this spec, research appendix
```

14 spec directories: 5 themes + 4 icons + 4 apps + 1 kernel. One repo, one COPR,
one git history. `llama.cpp` already demonstrates the subpackage pattern in-repo
(`base` / `-vulkan` / `-rocm`).

README.md paths, the specs table, the per-spec build sections, the
quick-reference table, and the linting section all need updating in the same
change (per CLAUDE.md).

## 6. Pilot

`fluent-gtk-theme` — exercises rename, variant subpackaging, directory move, and
a COPR package rename together. It is also the *least* representative of the
five on variant shape (the only one with no DPI axis to exclude), so the second
package converted should be Colloid or Orchis to prove the DPI exclusion before
the rest follow.

Gates, unchanged from CLAUDE.md:

- `mock -r fedora-44-x86_64 <srpm>` exit 0
- `rpmlint -c rpmlint.toml */*.spec` at 0 errors, 0 warnings
- `%check` passes for **every** built variant

## 7. Verification results (2026-07-19)

Measured against a patched Fluent tree built with `./install.sh -t all -i gnome
--tweaks solid round` (54 directories):

1. **`%check` holds across all variants.** It already globs `*/gtk-4.0/*.css`
   and `*/gnome-shell/gnome-shell.css`, so it loops variants without
   modification. Run verbatim over the full set: GTK4 `GtkCssProvider` parse of
   **108 CSS files, 0 real errors**; node-gate over **54 `gnome-shell.css`, 0
   misses** — every one carries both `.a11y-button` and
   `.message-list-clear-button`. Re-confirmed with raw `rtk proxy grep`.
2. **Patches hold for non-grey accents.** All three apply `-p1` clean to
   pristine source and their effects are present in all 54 compiled variants.
   Patch2's gate: **0** files retain a keyword `background-position`, and
   `background-position: 0 0` is present. The patches edit shared SCSS, so
   accent choice does not affect them.
3. **Build time and storage under the constrained set.** Fluent's full 54-variant
   run took **22.5 s** at 31.7 MB peak RSS, so build time is not a constraint at
   any of these scales. Storage, measured on the constrained builds:

   | Package | Compressed | Files | Symlinks |
   |---|---|---|---|
   | qogir-icon-theme | 4 MB | 20,581 | 25,316 |
   | whitesur-icon-theme | 16 MB | 60,735 | 68,838 |
   | tela-icon-theme | 10 MB | 57,513 | 80,151 |
   | tela-circle-icon-theme | 9 MB | 57,405 | 80,145 |
   | **icon total** | **39 MB** | **196,234** | **254,450** |

   Against the unconstrained matrices (163.3 MB, 818,538 files, 1,083,942
   symlinks), the colour constraint cuts storage ~4x and filesystem entries from
   ~1.9 M to ~450 K. Icon themes remain the dominant cost — Fluent's whole
   18-subpackage GTK set is 4.14 MB. Per-subpackage compression costs 3.3x for
   GTK themes (variants share content) but only 0.99x for icon themes (colour
   variants are genuinely distinct).

   The four non-Fluent GTK themes were **not** size-measured, only counted.
4. **The libadwaita user-CSS mechanism still works on GNOME 50.2.** With
   libadwaita **1.9.2** / GTK **4.22.4** on a live Wayland session, an
   `Adw.ApplicationWindow` label resolved to `rgb(0,0,6)` under an empty
   `XDG_CONFIG_HOME` and to `rgb(1,2,3)` when `$XDG_CONFIG_HOME/gtk-4.0/gtk.css`
   set that color — user CSS still overrides the libadwaita stylesheet.

Item 4 does **not** reverse the section 4 decision. It confirms the mechanism is
real, but it is a per-user action against `$HOME`; an RPM must not perform it at
build time. Document it as an optional post-install step instead.

### 7.5 Remaining items, now verified

**Patches and `%check` for the four non-Fluent GTK themes.** Each extracted
fresh, all its downstream patches applied `-p1`, built with the constrained
colour set, then run through the same two gates:

| Project | Patches | gtk-4.0 CSS | CSS errors | shell CSS | node-gate misses |
|---|---|---|---|---|---|
| colloid-gtk-theme | 3/3 clean | 18 | 0 | 9 | 0 |
| orchis-gtk-theme | 4/4 clean | 36 | 0 | 18 | 0 |
| qogir-gtk-theme | 2/2 clean | 6 | 0 | 3 | 0 |
| whitesur-gtk-theme | 4/4 clean | 24 | 0 | 12 | 0 |

**`mock` and `rpmlint` at multi-subpackage scale.** A prototype
`fluent-gtk-theme.spec` with 6 colour/size subpackages was built end to end:

- `mock -r fedora-44-x86_64` **exit 0 in 40-55 s** across three rebuilds.
- `%check` ran inside mock: 36 CSS files / 0 errors, node-gate OK, strip gate OK.
- Output: **7 binary RPMs** (1 main + 6 subpackages), **2.23 MB** total; each
  colour subpackage is 380 KB, the main package 20 KB.
- `rpmlint -c rpmlint.toml <spec>`: **0 errors, 0 warnings** — the CLAUDE.md gate
  lints specs only and passes unchanged.
- `rpmlint` on the **built RPMs** does *not* pass by default. It reported 2
  spelling errors (`colour`, `subpackage` — fixed by using US spelling and
  rewording) and `no-documentation` on all 7 packages. Adding `%license COPYING`
  to each subpackage cleared the errors but introduced 6 `files-duplicate`
  warnings, because `install.sh` drops its own `COPYING` into every theme dir;
  deleting those in `%install` resolves it. What remains is `no-documentation`
  on all 7, which `%license` does not satisfy.

  Resolution: a scoped filter, following the existing
  `llama.cpp-(vulkan|rocm).*no-documentation` precedent in `rpmlint.toml`:

  ```
  "(colloid|fluent|orchis|qogir|whitesur)-(gtk|icon)-theme.*no-documentation",
  ```

  Verified: with that line added, the 7 RPMs lint **0 errors, 0 warnings**.

**Sizes of the four non-Fluent GTK themes** (constrained colour set,
`tar | zstd -19`, whole set as one archive — not per-subpackage RPMs):
Colloid 235 KB, Orchis 467 KB, Qogir 1122 KB, WhiteSur 430 KB.

Total binary RPMs across the repo will be **44**: 35 subpackages plus one main
package per source package.

### 7.6 Repodata and dnf cost

Measured locally with `createrepo_c`, which generates the same metadata COPR
does. Repo built from 11 real RPMs (6 Fluent colour/size + 3 WhiteSur-icon
colour + 2 main packages):

| Metric | Measured |
|---|---|
| Payload | 31.91 MB |
| Repodata | 506 KB (1.55% of payload) |
| of which `filelists.xml.zst` | 504 KB — repodata is essentially all filelists |
| Repodata per filesystem entry | 3.75 bytes (138,346 entries) |
| `dnf makecache` | 0.02 s |
| `dnf repoquery` | 0.02 s |
| Payload unpack, 3 icon RPMs | 1.92 s for 129,862 entries (~14.8 us/entry) |

Projected to the full 35-subpackage set (~484,000 entries: 450,684 measured for
the four constrained icon themes, plus ~33,000 extrapolated for the GTK themes):
**repodata ~1.8 MB, full-install unpack ~7 s**. Neither is a constraint. The
projection is arithmetic from the measured per-entry rates, not a built
44-package repo.

**Not tested:** nothing was pushed to COPR. COPR's own repodata generation,
mirror sync, and web UI behaviour at this package count remain unobserved.

### 7.7 The icon themes have no `%check` at all

The premise of the earlier open item was wrong: `qogir-icon-theme`,
`tela-icon-theme`, `tela-circle-icon-theme` and `whitesur-icon-theme` contain
**zero** `%check` sections (`grep -c '^%check'` returns 0 for all four). There
was nothing to verify. They are ungated today, and `rpmlint.toml`'s
`no-%check-section` filter — justified as "nothing meaningful to assert at build
time" — is now stale, since the GTK themes do assert plenty.

A prototype `whitesur-icon-theme.spec` with 3 colour subpackages and a real
`%check` was built: `mock` **exit 0 in 80.5 s**, 4 RPMs (3 x 9.9 MB + 20 KB
main). Its gates:

- every installed theme carries an `index.theme` — 9/9 pass;
- a dangling-symlink census.

**The census found a real, pre-existing upstream defect.** Broken symlinks per
theme variant:

| Package | installed RPM (today) | dirs | per dir | constrained build | dirs | per dir |
|---|---|---|---|---|---|---|
| whitesur-icon-theme | 83 | 3 | 27.67 | 249 | 9 | **27.67** |
| tela-icon-theme | 2 | 3 | 0.67 | 6 | 9 | **0.67** |
| tela-circle-icon-theme | 4 | 3 | 1.33 | 12 | 9 | **1.33** |
| qogir-icon-theme | 0 | - | 0 | 0 | - | **0** |

The rates are identical, which proves the colour constraint neither causes nor
worsens them — these already ship in the COPR today. Causes seen in the data:
self-referential links (`lm_studio.svg -> lm_studio.svg`), two-node loops
(`tubefeeder.svg <-> de.schmidhuberj.tubefeeder.svg`), and 216 links to a
missing `weather-clear-night.svg`.

`rpmlint` corroborates independently: **246 `dangling-relative-symlink`
warnings, 0 errors** on the built icon RPMs.

**Resolved by downstream patches, not tolerated.** The ceiling approach was
replaced: each affected spec now carries a `fix-dangling-symlinks.patch` and a
`%check` gating at **zero**. Shipped in `tela-icon-theme`,
`tela-circle-icon-theme` and `whitesur-icon-theme` (all `Release: 2`);
`qogir-icon-theme` needs none.

| Package | Defect | Fix | Dangling |
|---|---|---|---|
| whitesur-icon | `install.sh` copied `links/` over installed icons with `cp -r`, so any alias sharing a name with a real icon replaced it with a symlink to itself | `cp -rn` | |
| whitesur-icon | `src/status/22` has no `weather-clear-night.svg`, but `links/status/22` holds 36 aliases pointing at it | supply it from the 32px source | 249 -> **0** |
| tela-icon | `xsi-addon-symbolic.svg` targets a sibling; the icon is in `symbolic/mimetypes` | repoint | 6 -> **0** |
| tela-circle | same, plus `CherryStudio.svg` whose symlink target carries a literal trailing newline (`"cherrystudio.svg\n"`, 17 bytes vs 16), plus `org.xfce.appfinder.svg` targeting `edit-find.svg` which exists only under `16/22/24/actions` | repoint, recreate, drop the dead alias | 12 -> **0** |

These are repairs, not deletions: the whitesur fix **restores ten app icons that
previously shipped as broken self-links** (affinity, bold-brew, gittyup, helium,
HTTrack, HTTrack-download, lm_studio, VirusTotal and the tubefeeder pair) as real
SVG files, and makes all 36 weather aliases resolve.

Verified: all three patches apply `-p1` clean, `mock` exit 0 for all three, and
the in-build gate reports `dangling-symlink gate: OK (0 across 3 themes)` for
each. `rpmlint -c rpmlint.toml */*.spec` stays at **0 errors, 0 warnings** across
all 14 specs.

Two RPM-level `rpmlint` findings remain and are **not** regressions:

- 10 `dangling-relative-symlink` warnings are **false positives**. rpmlint does
  not follow intermediate *directory* symlinks (e.g.
  `WhiteSur-dark/status/22 -> ../../WhiteSur/status/22`). All 10 were resolved
  individually on disk and every one resolves.
- `standard-dir-owned-by-package /usr/share/icons` is pre-existing: it comes from
  `%files %{_datarootdir}/icons`, which these changes did not touch. The proper
  fix is to own only the theme directories, and it is out of scope here.

## 8. Status: verified, with three named exclusions

Every design decision in this document is backed by a command run on this host.
The dangling-symlink work has landed as shipped patches (section 7.7) and is no
longer part of the open design.

What is **not** verified, and cannot be closed by further local work:

1. **COPR-side behaviour at 44 packages** — repodata generation, mirror sync and
   web UI. Nothing has been pushed. Local `createrepo_c` (section 7.6) measures
   the same metadata format but not COPR's own pipeline.
2. **The appendix survey.** Every claim except the `adw-gtk3` Fedora version comes
   from `docs/theme-research-2026-07.md`, not independently re-verified here. Its
   own caveats apply, notably that COPR absence is unproven because the search
   API matches project names rather than built package names.
3. **Two figures are arithmetic, not measurement**, and are labelled as such where
   they appear: the 44-package repodata projection (section 7.6, extrapolated
   from measured per-entry rates) and the compressed size of the four non-Fluent
   GTK themes as *RPMs* (section 7.5 gives `tar | zstd` of the whole set; only
   Fluent was built into actual subpackage RPMs).

Everything else — variant matrices, the DPI axis, the colour vocabulary, naming
convention, subpackage counts, `%check` behaviour, patch application, `mock`
exit status, `rpmlint` results, `-l` semantics, and the component-stripping
decision — was measured, and the command and its output are recorded above.

Implementation has not started beyond the pilot prototypes and the three
dangling-symlink patches, which are already in the repo.

**Update (2026-07-20): implementation complete.** All 9 theme/icon sources in
this design are converted: 5 GTK themes and 4 icon themes, each with the
`%check` gates and rpmlint filters described above. The 9 sources produce 42
binary packages (9 main + 33 color/size subpackages: colloid, fluent, orchis
and whitesur-gtk at 6 each = 24; tela, tela-circle and whitesur-icon at 3 each
= 9; qogir-gtk and qogir-icon ship no subpackages). `rpmlint -c rpmlint.toml
*/*/*.spec` reports 0 errors, 0 warnings. The three named exclusions above
(COPR-side behaviour, the appendix survey, the two arithmetic figures) remain
unverified — implementation did not touch them.

## Appendix: non-vinceliuice alternatives

Full report with citations: `docs/theme-research-2026-07.md`.

- **adw-gtk3** is the only theme with an unambiguous GNOME 50 statement: v6.5
  (2026-04-13) release body reads verbatim *"Release for GNOME 50."* Fedora ships
  `adw-gtk3-theme 6.4-3.fc44` — confirmed by `dnf repoquery` on this host, one
  release behind, so F44 users get the pre-GNOME-50 stylesheet. Clearest
  packaging gap found.
- **MoreWaita** is the best icon target: GNOME-tracking version scheme, commits
  to 2026-06-23, ships `meson.build` and `PACKAGING.md`, ~13.5 MiB, not in
  Fedora.
- **Nordic** has commit-level GNOME 50 fixes (2026-05-04, nautilus pathbar and
  sidebar) but a 2022 release tag.
- Blocked: `Delta-Icons/linux` is CC-BY-NC-ND-4.0 (non-free);
  `GNOME-macOS-Tahoe` declares no license at all.
- `catppuccin/gtk` is archived (2024-06-02). `Celestial`'s README says
  "GNOME Shell 38-48" — explicit negative evidence.
- Papirus is already in Fedora at the current upstream tag; repackaging adds
  nothing.

Every claim in this appendix except the `adw-gtk3` Fedora version is sourced
from the linked report, not independently re-verified here. The report's own
caveats apply — in particular, COPR absence is not proven, since its search API
matches project names rather than built package names.

The report's open question about `~/.config/gtk-4.0/gtk.css` has since been
**settled affirmatively** (section 7, item 4; libadwaita 1.9.2, not the 1.8 the
report assumed). Themes relying on that mechanism are not disqualified by it.
