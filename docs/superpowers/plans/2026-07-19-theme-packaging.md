# Theme/Icon Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert 9 vinceliuice theme/icon source packages into 35 colour/size
variant subpackages, standardize three package names, and group the repo by
category.

**Architecture:** Each source package keeps one `install.sh` invocation
constrained to blue+red+grey, deletes the DPI and non-GNOME payload in
`%install`, and lists each accent's light/dark/standard triple as one
`%package`. The main package ships only `%license`. No `Obsoletes`/`Provides`:
renames are a clean break, with old COPR packages deleted via `copr-cli`.

**Tech Stack:** RPM spec files, `mock` (fedora-44-x86_64), `rpmlint`,
`spectool`, `copr-cli`, GNOME 50.2 / GTK 4.22 on Fedora 44.

**Design spec:** `docs/superpowers/specs/2026-07-19-theme-packaging-design.md`

**Deviation from the spec, deliberate:** the spec projects 44 binary RPMs (35
variant packages + one main per source). This plan produces **42**, because
`qogir-gtk-theme` and `qogir-icon-theme` have no accent axis and ship their three
directories directly rather than as a license-only main plus one variant
subpackage. A main package that exists only to hold `%license` for a single
variant is pointless. Per-source counts:

| Source | Binary RPMs |
|---|---|
| fluent-gtk-theme | 7 (1 main + 6) |
| colloid-gtk-theme | 7 (1 main + 6) |
| orchis-gtk-theme | 7 (1 main + 6) |
| whitesur-gtk-theme | 7 (1 main + 6) |
| qogir-gtk-theme | 1 |
| whitesur-icon-theme | 4 (1 main + 3) |
| tela-icon-theme | 4 (1 main + 3) |
| tela-circle-icon-theme | 4 (1 main + 3) |
| qogir-icon-theme | 1 |
| **total** | **42** |

## Global Constraints

- Target is Fedora 44, GNOME 50.2, GTK 4.22. Build in a clean chroot only.
- Colours are exactly **blue, red, grey**. Upstream spells blue `default` in
  Colloid, Fluent, Orchis, Qogir and WhiteSur-icon; the subpackage is still
  named `-blue`. Qogir has no accent axis and ships its default as one package.
- **Never ship `-hdpi`/`-xhdpi`.** They contain only `xfwm4/` — no `gtk-4.0`, no
  `gnome-shell`, no `index.theme`. Delete them in `%install`.
- **Never ship `cinnamon`, `xfwm4`, `plank`, `unity`.** Keep `gtk-2.0` (246 GTK2
  apps remain in F44) and `metacity-1` (gnome-flashback is an installable GNOME
  session).
- Do not pass `-l`/`--libadwaita`. It writes only to the builder's `$HOME` and
  contributes no files. Exception on record: `colloid -l fixed` *does* alter
  output; it is never used here.
- Downstream patch or packaging change → bump `Release`, keep upstream
  `Version`. Use `%autosetup -p1` whenever a `PatchN:` is present.
- `%changelog`: escape macros as `%%` (e.g. `%%autosetup`, `%%{_datarootdir}`).
  Header format: `* Day Mon DD YYYY Name <email> - VERSION-RELEASE`.
- `%files` must never list `%{_datarootdir}/themes` or `%{_datarootdir}/icons`
  themselves — those belong to the `filesystem` package.
- **Stage patches one spec at a time.** `~/rpmbuild/SOURCES/` is flat and patch
  basenames collide across specs (five ship `gnome50-selectors.patch`, three
  ship `fix-dangling-symlinks.patch`). Staging all at once builds a spec against
  another's patch and fails as a bogus "hunk FAILED".
- **Use `rtk proxy` for any `grep`/`ls` whose output is consumed
  programmatically.** The rtk hook rewrites their output and silently corrupts
  `$(grep ...)` substitution.
- This shell is zsh: unquoted parameter expansion does not word-split, and an
  unmatched glob aborts the whole command.
- Gate for every task: `mock` exit 0 **and** `rpmlint -c rpmlint.toml` over all
  specs reporting `0 errors, 0 warnings`. The glob depth changes in Task 1:
  before it, `*/*.spec`; from Task 1 onward, `*/*/*.spec`. Every task from 2
  onward uses `*/*/*.spec`.
- Working branch is `develop`. Commit per task.

---

## File Structure

```
themes/colloid-gtk-theme/     colloid-gtk-theme.spec + 3 patches
themes/fluent-gtk-theme/      fluent-gtk-theme.spec + 3 patches   (renamed)
themes/orchis-gtk-theme/      orchis-gtk-theme.spec + 4 patches   (renamed)
themes/qogir-gtk-theme/       qogir-gtk-theme.spec + 2 patches    (renamed)
themes/whitesur-gtk-theme/    whitesur-gtk-theme.spec + 4 patches
icons/qogir-icon-theme/       qogir-icon-theme.spec
icons/tela-icon-theme/        tela-icon-theme.spec + 1 patch
icons/tela-circle-icon-theme/ tela-circle-icon-theme.spec + 1 patch
icons/whitesur-icon-theme/    whitesur-icon-theme.spec + 1 patch
apps/mural/                   mural.spec + mural.1
apps/gnome-shell-extension-per-monitor-wallpaper/
apps/looking-glass-client/
apps/llama.cpp/
kernel/looking-glass-kvmfr-kmod/
docs/                         spec, plan, research appendix
rpmlint.toml                  gains one filter line (Task 2)
README.md                     paths + tables (Tasks 1 and 11)
```

Each spec is self-contained: one `install.sh` call, one `%install` cleanup
block, one `%check`, one `%package`/`%files` pair per colour-size combination.

---

### Task 1: Reorganize the repo into category directories

Pure `git mv`. No spec content changes, so any build failure means a path
mistake, not a packaging one.

**Files:**
- Move: all 14 spec directories into `themes/`, `icons/`, `apps/`, `kernel/`
- Modify: `README.md` (paths only)

**Interfaces:**
- Produces: every later task addresses specs at `<category>/<pkg>/<pkg>.spec`.

- [ ] **Step 1: Create the category directories and move everything**

```bash
cd /home/ekthor/Projects/rpm-specs
mkdir -p themes icons apps kernel
git mv colloid-gtk-theme fluent-gtk-theme orchis-theme qogir-theme whitesur-gtk-theme themes/
git mv qogir-icon-theme tela-icon-theme tela-circle-icon-theme whitesur-icon-theme icons/
git mv mural gnome-shell-extension-per-monitor-wallpaper looking-glass-client llama.cpp apps/
git mv looking-glass-kvmfr-kmod kernel/
```

- [ ] **Step 2: Verify all 14 specs are found at the new depth**

Run:
```bash
find themes icons apps kernel -name '*.spec' | wc -l
```
Expected: `14`

- [ ] **Step 3: Update the lint gate command in README.md**

The gate must reach one level deeper. Replace every occurrence of
`*/*.spec` with `*/*/*.spec` in `README.md`, and update the "Repo layout"
section to describe the four category directories.

- [ ] **Step 4: Run the lint gate at the new depth**

Run:
```bash
cd /home/ekthor/Projects/rpm-specs
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
```
Expected: `0 packages and 14 specfiles checked; 0 errors, 0 warnings`

- [ ] **Step 5: Build one spec to prove paths still resolve**

Run:
```bash
cd /home/ekthor/Projects/rpm-specs
cp icons/qogir-icon-theme/*.patch ~/rpmbuild/SOURCES/ 2>/dev/null || true
spectool -g -R icons/qogir-icon-theme/qogir-icon-theme.spec
rpmbuild -bs icons/qogir-icon-theme/qogir-icon-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/qogir-icon-theme-20250215-4.fc44.src.rpm
echo "mock exit=$?"
```
Expected: `mock exit=0`

- [ ] **Step 6: Commit**

```bash
cd /home/ekthor/Projects/rpm-specs
git add -A
git commit -m "repo: group specs into themes/ icons/ apps/ kernel/

Directory move only; no spec content changes. The lint gate becomes
*/*/*.spec. Verified: 14 specs found at the new depth, gate reports
0 errors 0 warnings, and qogir-icon-theme still builds in mock.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Pilot — rename fluent-gtk-theme-compact and split into 6 subpackages

The pilot exercises rename, subpackaging, the `%install` cleanup idiom, the
rpmlint filter and the COPR rename together. A working prototype already exists
at `scratchpad/proto/fluent-gtk-theme.spec`; this task lands it properly.

Fluent is the only GTK theme **without** a DPI axis, so its `%install` needs no
hdpi deletion. Task 3 introduces that.

**Files:**
- Create: `themes/fluent-gtk-theme/fluent-gtk-theme.spec`
- Delete: `themes/fluent-gtk-theme/fluent-gtk-theme-compact.spec`
- Modify: `rpmlint.toml`

**Interfaces:**
- Produces: the `%install` cleanup block, the `%check` gates, and the
  `-blue`/`-red`/`-grey` subpackage naming that Tasks 3-10 reuse.
- Produces: the `rpmlint.toml` filter line that every later task depends on to
  keep RPM-level lint clean.

- [ ] **Step 1: Add the rpmlint filter for theme subpackages**

Theme subpackages ship no docs by design; `%license` does not satisfy
rpmlint's documentation check. Add one line to the `Filters` list in
`rpmlint.toml`, following the existing `llama.cpp-(vulkan|rocm)` precedent, and
document it in the comment block above:

```toml
    "(colloid|fluent|orchis|qogir|whitesur)-(gtk|icon)-theme.*no-documentation",
```

- [ ] **Step 2: Write the new spec**

Create `themes/fluent-gtk-theme/fluent-gtk-theme.spec`:

```spec
Name:           fluent-gtk-theme
Version:        20250417
Release:        9%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Fluent-gtk-theme
%define dversion 2025-04-17
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz
Patch0:         gnome50-selectors.patch
Patch1:         gnome50-appearance.patch
# St's shell CSS engine rejects the keyword value in the upstream
# #panelActivities "background-position: center center" (logged at runtime as
# "Ignoring length property that isn't a number"). St already falls back to 0 0,
# so the numeric form is pixel-identical and silences the warning.
Patch2:         fix-shell-bg-position.patch

BuildRequires:  gnome-shell
BuildRequires:  sassc
# %%check: validate the compiled GTK4 CSS with the real GTK engine
BuildRequires:  gtk4
BuildRequires:  python3-gobject-base

%description
Fluent is a Fluent design theme for GNOME/GTK based desktop environments.
This package ships the license only; install a colour package for the theme.

# Upstream spells the blue accent "default"; packages are named for the colour.
%package blue
Summary:        Fluent GTK theme, blue accent
%description blue
Blue accent, standard size. Ships light, dark and auto variants.

%package blue-compact
Summary:        Fluent GTK theme, blue accent, compact
%description blue-compact
Blue accent, compact size. Ships light, dark and auto variants.

%package red
Summary:        Fluent GTK theme, red accent
%description red
Red accent, standard size. Ships light, dark and auto variants.

%package red-compact
Summary:        Fluent GTK theme, red accent, compact
%description red-compact
Red accent, compact size. Ships light, dark and auto variants.

%package grey
Summary:        Fluent GTK theme, grey accent
%description grey
Grey accent, standard size. Ships light, dark and auto variants.

%package grey-compact
Summary:        Fluent GTK theme, grey accent, compact
%description grey-compact
Grey accent, compact size. Ships light, dark and auto variants.

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# -s defaults to all sizes. -l omitted: it writes only to $HOME and adds no
# files to the buildroot.
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  -t default -t red -t grey -i gnome --tweaks solid round
# Desktops this COPR does not target. gtk-2.0 and metacity-1 are kept: 246 GTK2
# apps remain in F44, and gnome-flashback/metacity are installable GNOME
# sessions.
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
# install.sh drops a COPYING into every theme dir; %%license ships one copy per
# package under %%{_licensedir}, so the in-tree duplicates are redundant.
find %{buildroot}%{_datarootdir}/themes -name COPYING -delete

%check
python3 - <<'PYEOF'
import gi, sys, glob
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
real = 0
cur = ""
def on_err(prov, section, err):
    global real
    if "does not exist" in err.message:
        return
    loc = section.get_start_location()
    sys.stderr.write("CSS ERROR " + cur + ":" + str(loc.lines + 1) + ": " + err.message + "\n")
    real += 1
files = sorted(glob.glob("%{buildroot}%{_datadir}/themes/*/gtk-4.0/*.css"))
assert files, "no gtk-4.0 css found to validate"
for cur in files:
    prov = Gtk.CssProvider()
    prov.connect("parsing-error", on_err)
    prov.load_from_path(cur)
print("GTK4 CSS parse check: " + str(len(files)) + " file(s), " + str(real) + " real error(s)")
sys.exit(1 if real else 0)
PYEOF
for css in %{buildroot}%{_datadir}/themes/*/gnome-shell/gnome-shell.css; do
  grep -q 'a11y-button' "$css" || { echo "node-gate FAIL: .a11y-button missing in $css"; exit 1; }
  grep -q 'message-list-clear-button' "$css" || { echo "node-gate FAIL: .message-list-clear-button missing in $css"; exit 1; }
done
echo "shell node-gate: OK"
for d in cinnamon xfwm4 plank unity; do
  found=$(find %{buildroot}%{_datadir}/themes -maxdepth 2 -type d -name "$d" | wc -l)
  [ "$found" -eq 0 ] || { echo "strip FAIL: $found $d dirs remain"; exit 1; }
done
echo "strip gate: OK"

%files
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/themes/Fluent-round
%{_datarootdir}/themes/Fluent-round-Light
%{_datarootdir}/themes/Fluent-round-Dark

%files blue-compact
%license COPYING
%{_datarootdir}/themes/Fluent-round-compact
%{_datarootdir}/themes/Fluent-round-Light-compact
%{_datarootdir}/themes/Fluent-round-Dark-compact

%files red
%license COPYING
%{_datarootdir}/themes/Fluent-round-red
%{_datarootdir}/themes/Fluent-round-red-Light
%{_datarootdir}/themes/Fluent-round-red-Dark

%files red-compact
%license COPYING
%{_datarootdir}/themes/Fluent-round-red-compact
%{_datarootdir}/themes/Fluent-round-red-Light-compact
%{_datarootdir}/themes/Fluent-round-red-Dark-compact

%files grey
%license COPYING
%{_datarootdir}/themes/Fluent-round-grey
%{_datarootdir}/themes/Fluent-round-grey-Light
%{_datarootdir}/themes/Fluent-round-grey-Dark

%files grey-compact
%license COPYING
%{_datarootdir}/themes/Fluent-round-grey-compact
%{_datarootdir}/themes/Fluent-round-grey-Light-compact
%{_datarootdir}/themes/Fluent-round-grey-Dark-compact

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250417-9
- Rename from fluent-gtk-theme-compact: "compact" is a size variant, not a
  source package. Fedora expresses variants as subpackages
  (numix-icon-theme-circle, papirus-icon-theme-dark), never as separate source
  packages. Clean break, no Obsoletes/Provides.
- Split into colour/size packages (blue, red, grey x standard, compact). Blue is
  upstream's "default" accent; the package is named for the colour.
- Drop -l/--libadwaita. Verified byte-identical buildroots with and without it:
  it only writes $HOME/.config/gtk-4.0 and adds no files to the RPM. The
  20250417-3 changelog claim that it enabled GTK4/libadwaita theming was wrong
  in packaging terms.
- Strip cinnamon/xfwm4/plank/unity: this COPR targets GNOME only. gtk-2.0 and
  metacity-1 are kept deliberately.
- Extend %%check with a strip gate.
```

- [ ] **Step 3: Remove the old spec and stage sources**

```bash
cd /home/ekthor/Projects/rpm-specs
git rm -q themes/fluent-gtk-theme/fluent-gtk-theme-compact.spec
cp themes/fluent-gtk-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R themes/fluent-gtk-theme/fluent-gtk-theme.spec
```

- [ ] **Step 4: Build and verify the gates**

```bash
cd /home/ekthor/Projects/rpm-specs
rpmbuild -bs themes/fluent-gtk-theme/fluent-gtk-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/fluent-gtk-theme-20250417-9.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'GTK4 CSS parse|node-gate|strip gate' /var/lib/mock/fedora-44-x86_64/result/build.log
```
Expected: `mock exit=0`, `36 file(s), 0 real error(s)`, `shell node-gate: OK`,
`strip gate: OK`

- [ ] **Step 5: Verify the package set and that no hdpi or foreign payload shipped**

```bash
R=/var/lib/mock/fedora-44-x86_64/result
rtk proxy ls -1 $R | rtk proxy grep 'noarch.rpm'
rpm -qlp $R/fluent-gtk-theme-blue-20250417-9.fc44.noarch.rpm | \
  rtk proxy grep -oE '/themes/[^/]+/[^/]+$' | sed 's|.*/||' | sort -u
```
Expected: 7 noarch RPMs (1 main + 6 colour/size). Second command lists exactly
`gnome-shell`, `gtk-2.0`, `gtk-3.0`, `gtk-4.0`, `index.theme`, `metacity-1`.

- [ ] **Step 6: Run both lint gates**

```bash
cd /home/ekthor/Projects/rpm-specs
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
rpmlint -c rpmlint.toml /var/lib/mock/fedora-44-x86_64/result/*.noarch.rpm 2>&1 | tail -2
```
Expected: specs `0 errors, 0 warnings`. RPMs `0 errors, 0 warnings`.

- [ ] **Step 7: Rename the package in COPR**

```bash
copr-cli delete-package wdm --name fluent-gtk-theme-compact
copr-cli list-packages wdm | rtk proxy grep '"name"'
```
Expected: `fluent-gtk-theme-compact` absent from the list.

- [ ] **Step 8: Commit**

```bash
cd /home/ekthor/Projects/rpm-specs
git add rpmlint.toml themes/fluent-gtk-theme/
git commit -m "fluent-gtk-theme: rename from -compact, split into colour/size packages

'compact' was a size variant promoted to a source package name, and the
directory disagreed with Name:. Fedora ships variants as subpackages
(numix-icon-theme-circle, papirus-icon-theme-dark). Clean break, no
Obsoletes/Provides; the old COPR package is deleted.

6 colour/size packages (blue, red, grey x standard, compact), main package
ships %license only. Drops -l (verified no-op) and strips non-GNOME payload.

Verified: mock exit 0, 36 CSS files 0 errors, node-gate and strip gate OK,
7 RPMs, both lint gates 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: colloid-gtk-theme — 6 subpackages, introduces DPI deletion

Colloid emits `-hdpi`/`-xhdpi` (81 dirs at `-t all`). Those directories contain
only `xfwm4/`, so they must be deleted in `%install` or `rpmbuild` will fail
with unpackaged files. Colloid also needs **two** `install.sh` calls: its `-s`
takes one value at a time and defaults to `standard` only.

**Files:**
- Modify: `themes/colloid-gtk-theme/colloid-gtk-theme.spec`

**Interfaces:**
- Consumes: the rpmlint filter from Task 2.
- Produces: the hdpi-deletion idiom and its `%check` gate, reused by Tasks 4-6.

- [ ] **Step 1: Add the hdpi gate to `%check` first, and build to watch it fail**

Append to the existing `%check` in
`themes/colloid-gtk-theme/colloid-gtk-theme.spec`:

```bash
hdpi=$(find %{buildroot}%{_datadir}/themes -maxdepth 1 -type d \
  \( -name '*-hdpi' -o -name '*-xhdpi' \) | wc -l)
[ "$hdpi" -eq 0 ] || { echo "dpi gate FAIL: $hdpi hdpi dir(s) remain"; exit 1; }
echo "dpi gate: OK"
```

Then build:
```bash
cd /home/ekthor/Projects/rpm-specs
cp themes/colloid-gtk-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R themes/colloid-gtk-theme/colloid-gtk-theme.spec
rpmbuild -bs themes/colloid-gtk-theme/colloid-gtk-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/colloid-gtk-theme-20250731-6.fc44.src.rpm
rtk proxy grep 'dpi gate' /var/lib/mock/fedora-44-x86_64/result/build.log
```
Expected: build FAILS with `dpi gate FAIL: 18 hdpi dir(s) remain` (the current
spec ships one colour, producing 18 DPI dirs).

- [ ] **Step 2: Rewrite `%install` to constrain colours and delete DPI/foreign payload**

Replace the `%install` body with:

```spec
%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# -s takes one value per call and defaults to standard, so run it twice.
# -l omitted: verified no-op for the buildroot (note: -l fixed is NOT a no-op,
# but is not used here).
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  -t default -t red -t grey -s standard
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  -t default -t red -t grey -s compact
# -hdpi/-xhdpi contain only xfwm4 assets: no gtk-4.0, no gnome-shell, not even
# an index.theme. They are unusable on GNOME.
rm -rf %{buildroot}%{_datarootdir}/themes/*-hdpi
rm -rf %{buildroot}%{_datarootdir}/themes/*-xhdpi
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
find %{buildroot}%{_datarootdir}/themes -name COPYING -delete
```

- [ ] **Step 3: Bump Release, add the subpackages and `%files`**

Set `Release: 7%{?dist}`. Add after `%description`:

```spec
%package blue
Summary:        Colloid GTK theme, blue accent
%description blue
Blue accent, standard size. Ships light, dark and auto variants.

%package blue-compact
Summary:        Colloid GTK theme, blue accent, compact
%description blue-compact
Blue accent, compact size. Ships light, dark and auto variants.

%package red
Summary:        Colloid GTK theme, red accent
%description red
Red accent, standard size. Ships light, dark and auto variants.

%package red-compact
Summary:        Colloid GTK theme, red accent, compact
%description red-compact
Red accent, compact size. Ships light, dark and auto variants.

%package grey
Summary:        Colloid GTK theme, grey accent
%description grey
Grey accent, standard size. Ships light, dark and auto variants.

%package grey-compact
Summary:        Colloid GTK theme, grey accent, compact
%description grey-compact
Grey accent, compact size. Ships light, dark and auto variants.
```

Replace `%files` with (directory names verified by a real build):

```spec
%files
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/themes/Colloid
%{_datarootdir}/themes/Colloid-Light
%{_datarootdir}/themes/Colloid-Dark

%files blue-compact
%license COPYING
%{_datarootdir}/themes/Colloid-Compact
%{_datarootdir}/themes/Colloid-Light-Compact
%{_datarootdir}/themes/Colloid-Dark-Compact

%files red
%license COPYING
%{_datarootdir}/themes/Colloid-Red
%{_datarootdir}/themes/Colloid-Red-Light
%{_datarootdir}/themes/Colloid-Red-Dark

%files red-compact
%license COPYING
%{_datarootdir}/themes/Colloid-Red-Compact
%{_datarootdir}/themes/Colloid-Red-Light-Compact
%{_datarootdir}/themes/Colloid-Red-Dark-Compact

%files grey
%license COPYING
%{_datarootdir}/themes/Colloid-Grey
%{_datarootdir}/themes/Colloid-Grey-Light
%{_datarootdir}/themes/Colloid-Grey-Dark

%files grey-compact
%license COPYING
%{_datarootdir}/themes/Colloid-Grey-Compact
%{_datarootdir}/themes/Colloid-Grey-Light-Compact
%{_datarootdir}/themes/Colloid-Grey-Dark-Compact
```

Add the changelog entry:

```spec
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250731-7
- Split into colour/size packages (blue, red, grey x standard, compact). Blue is
  upstream's "default" accent; packages are named for the colour.
- Drop -hdpi/-xhdpi: those directories hold only xfwm4 assets (no gtk-4.0, no
  gnome-shell, no index.theme) and are unusable on GNOME. Gated in %%check.
- Strip cinnamon/xfwm4/plank/unity; keep gtk-2.0 and metacity-1.
- Drop -l/--libadwaita: verified byte-identical buildroot without it.
```

- [ ] **Step 4: Rebuild and verify every gate passes**

```bash
cd /home/ekthor/Projects/rpm-specs
rpmbuild -bs themes/colloid-gtk-theme/colloid-gtk-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/colloid-gtk-theme-20250731-7.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'GTK4 CSS parse|node-gate|strip gate|dpi gate' /var/lib/mock/fedora-44-x86_64/result/build.log
rtk proxy ls -1 /var/lib/mock/fedora-44-x86_64/result | rtk proxy grep -c 'noarch.rpm'
```
Expected: `mock exit=0`; all four gates OK; `7` noarch RPMs.

- [ ] **Step 5: Run both lint gates**

```bash
cd /home/ekthor/Projects/rpm-specs
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
rpmlint -c rpmlint.toml /var/lib/mock/fedora-44-x86_64/result/*.noarch.rpm 2>&1 | tail -2
```
Expected: both `0 errors, 0 warnings`.

- [ ] **Step 6: Commit**

```bash
cd /home/ekthor/Projects/rpm-specs
git add themes/colloid-gtk-theme/
git commit -m "colloid-gtk-theme: split into colour/size packages, drop DPI variants

6 packages (blue, red, grey x standard, compact). -hdpi/-xhdpi are deleted in
%install: they contain only xfwm4 assets and are unusable on GNOME. A %check
gate asserts none survive.

Verified: mock exit 0, all four gates OK, 7 RPMs, both lint gates 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Rename orchis-theme to orchis-gtk-theme and split into 6 subpackages

Orchis emits both sizes from a single call, plus DPI dirs.

**Files:**
- Move: `themes/orchis-theme/` → `themes/orchis-gtk-theme/`
- Move: `orchis-theme.spec` → `orchis-gtk-theme.spec`

**Interfaces:**
- Consumes: hdpi-deletion idiom and gate from Task 3; rpmlint filter from Task 2.

- [ ] **Step 1: Rename directory and spec**

```bash
cd /home/ekthor/Projects/rpm-specs
git mv themes/orchis-theme themes/orchis-gtk-theme
git mv themes/orchis-gtk-theme/orchis-theme.spec themes/orchis-gtk-theme/orchis-gtk-theme.spec
```

- [ ] **Step 2: Set Name and Release, add subpackages**

In `themes/orchis-gtk-theme/orchis-gtk-theme.spec` set `Name: orchis-gtk-theme`
and `Release: 3%{?dist}`. Add after `%description`:

```spec
%package blue
Summary:        Orchis GTK theme, blue accent
%description blue
Blue accent, standard size. Ships light, dark and auto variants.

%package blue-compact
Summary:        Orchis GTK theme, blue accent, compact
%description blue-compact
Blue accent, compact size. Ships light, dark and auto variants.

%package red
Summary:        Orchis GTK theme, red accent
%description red
Red accent, standard size. Ships light, dark and auto variants.

%package red-compact
Summary:        Orchis GTK theme, red accent, compact
%description red-compact
Red accent, compact size. Ships light, dark and auto variants.

%package grey
Summary:        Orchis GTK theme, grey accent
%description grey
Grey accent, standard size. Ships light, dark and auto variants.

%package grey-compact
Summary:        Orchis GTK theme, grey accent, compact
%description grey-compact
Grey accent, compact size. Ships light, dark and auto variants.
```

- [ ] **Step 3: Rewrite `%install`**

```spec
%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# One call emits both sizes. -l omitted: verified no-op for the buildroot.
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  --icon gnome -t default -t red -t grey
rm -rf %{buildroot}%{_datarootdir}/themes/*-hdpi
rm -rf %{buildroot}%{_datarootdir}/themes/*-xhdpi
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
find %{buildroot}%{_datarootdir}/themes -name COPYING -delete
```

- [ ] **Step 4: Add the hdpi gate to `%check`**

Append to the existing `%check`:

```bash
hdpi=$(find %{buildroot}%{_datadir}/themes -maxdepth 1 -type d \
  \( -name '*-hdpi' -o -name '*-xhdpi' \) | wc -l)
[ "$hdpi" -eq 0 ] || { echo "dpi gate FAIL: $hdpi hdpi dir(s) remain"; exit 1; }
echo "dpi gate: OK"
```

- [ ] **Step 5: Write `%files` (names verified by a real build)**

```spec
%files
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/themes/Orchis
%{_datarootdir}/themes/Orchis-Light
%{_datarootdir}/themes/Orchis-Dark

%files blue-compact
%license COPYING
%{_datarootdir}/themes/Orchis-Compact
%{_datarootdir}/themes/Orchis-Light-Compact
%{_datarootdir}/themes/Orchis-Dark-Compact

%files red
%license COPYING
%{_datarootdir}/themes/Orchis-Red
%{_datarootdir}/themes/Orchis-Red-Light
%{_datarootdir}/themes/Orchis-Red-Dark

%files red-compact
%license COPYING
%{_datarootdir}/themes/Orchis-Red-Compact
%{_datarootdir}/themes/Orchis-Red-Light-Compact
%{_datarootdir}/themes/Orchis-Red-Dark-Compact

%files grey
%license COPYING
%{_datarootdir}/themes/Orchis-Grey
%{_datarootdir}/themes/Orchis-Grey-Light
%{_datarootdir}/themes/Orchis-Grey-Dark

%files grey-compact
%license COPYING
%{_datarootdir}/themes/Orchis-Grey-Compact
%{_datarootdir}/themes/Orchis-Grey-Light-Compact
%{_datarootdir}/themes/Orchis-Grey-Dark-Compact
```

Add the changelog entry:

```spec
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-3
- Rename to orchis-gtk-theme: -gtk-theme is the Fedora plurality for GTK themes
  and makes this repo internally consistent. Clean break, no Obsoletes/Provides.
- Split into colour/size packages (blue, red, grey x standard, compact).
- Drop -hdpi/-xhdpi (xfwm4-only, unusable on GNOME); gated in %%check.
- Strip cinnamon/xfwm4/plank/unity; keep gtk-2.0 and metacity-1.
- Drop -l/--libadwaita: verified byte-identical buildroot without it.
```

- [ ] **Step 6: Build and verify**

```bash
cd /home/ekthor/Projects/rpm-specs
cp themes/orchis-gtk-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R themes/orchis-gtk-theme/orchis-gtk-theme.spec
rpmbuild -bs themes/orchis-gtk-theme/orchis-gtk-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/orchis-gtk-theme-20260707-3.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'GTK4 CSS parse|node-gate|strip gate|dpi gate' /var/lib/mock/fedora-44-x86_64/result/build.log
```
Expected: `mock exit=0`, all four gates OK.

- [ ] **Step 7: Lint, COPR rename, commit**

```bash
cd /home/ekthor/Projects/rpm-specs
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
rpmlint -c rpmlint.toml /var/lib/mock/fedora-44-x86_64/result/*.noarch.rpm 2>&1 | tail -2
copr-cli delete-package wdm --name orchis-theme
git add -A themes/orchis-gtk-theme
git commit -m "orchis-gtk-theme: rename from orchis-theme, split into colour/size packages

-gtk-theme is the Fedora plurality for GTK themes and makes the repo
internally consistent. Clean break; old COPR package deleted.

6 colour/size packages, DPI variants dropped, non-GNOME payload stripped.
Verified: mock exit 0, all gates OK, both lint gates 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Rename qogir-theme to qogir-gtk-theme, one colour package

Qogir has **no accent axis** — `-t` selects distro branding (`default`,
`manjaro`, `ubuntu`), not colours. It therefore ships a single package with no
colour suffix. This is the intended asymmetry, not an oversight.

**Files:**
- Move: `themes/qogir-theme/` → `themes/qogir-gtk-theme/`
- Move: `qogir-theme.spec` → `qogir-gtk-theme.spec`

- [ ] **Step 1: Rename directory and spec**

```bash
cd /home/ekthor/Projects/rpm-specs
git mv themes/qogir-theme themes/qogir-gtk-theme
git mv themes/qogir-gtk-theme/qogir-theme.spec themes/qogir-gtk-theme/qogir-gtk-theme.spec
```

- [ ] **Step 2: Set Name, Release and `%install`**

Set `Name: qogir-gtk-theme`, `Release: 7%{?dist}`, and replace `%install`:

```spec
%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# -t selects distro branding, not accent colour, so only the default ships.
# -l omitted: verified no-op for the buildroot.
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  --icon gnome --tweaks round -t default
rm -rf %{buildroot}%{_datarootdir}/themes/*-hdpi
rm -rf %{buildroot}%{_datarootdir}/themes/*-xhdpi
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
find %{buildroot}%{_datarootdir}/themes -name COPYING -delete
```

- [ ] **Step 3: Add the hdpi gate to `%check`**

Append to the existing `%check`:

```bash
hdpi=$(find %{buildroot}%{_datadir}/themes -maxdepth 1 -type d \
  \( -name '*-hdpi' -o -name '*-xhdpi' \) | wc -l)
[ "$hdpi" -eq 0 ] || { echo "dpi gate FAIL: $hdpi hdpi dir(s) remain"; exit 1; }
echo "dpi gate: OK"
```

- [ ] **Step 4: Write `%files` (names verified by a real build)**

No subpackages: this package ships its three directories directly.

```spec
%files
%license COPYING
%{_datarootdir}/themes/Qogir
%{_datarootdir}/themes/Qogir-Light
%{_datarootdir}/themes/Qogir-Dark
```

Add the changelog entry:

```spec
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250817-7
- Rename to qogir-gtk-theme: -gtk-theme is the Fedora plurality for GTK themes.
  Clean break, no Obsoletes/Provides.
- No colour split: Qogir's -t selects distro branding (default|manjaro|ubuntu),
  not accent colour, so only the default variant ships.
- Drop -hdpi/-xhdpi (xfwm4-only, unusable on GNOME); gated in %%check.
- Strip cinnamon/xfwm4/plank/unity; keep gtk-2.0 and metacity-1.
- Drop -l/--libadwaita: verified byte-identical buildroot without it.
```

- [ ] **Step 5: Build, lint, COPR rename, commit**

```bash
cd /home/ekthor/Projects/rpm-specs
cp themes/qogir-gtk-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R themes/qogir-gtk-theme/qogir-gtk-theme.spec
rpmbuild -bs themes/qogir-gtk-theme/qogir-gtk-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/qogir-gtk-theme-20250817-7.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'GTK4 CSS parse|node-gate|strip gate|dpi gate' /var/lib/mock/fedora-44-x86_64/result/build.log
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
rpmlint -c rpmlint.toml /var/lib/mock/fedora-44-x86_64/result/*.noarch.rpm 2>&1 | tail -2
copr-cli delete-package wdm --name qogir-theme
git add -A themes/qogir-gtk-theme
git commit -m "qogir-gtk-theme: rename from qogir-theme, drop DPI variants

-gtk-theme is the Fedora plurality. Clean break; old COPR package deleted.

No colour split: Qogir's -t selects distro branding, not accent colour, so it
ships one package. DPI variants dropped, non-GNOME payload stripped.

Verified: mock exit 0, all gates OK, both lint gates 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: `mock exit=0`, all four gates OK, both lint gates `0 errors, 0 warnings`.

---

### Task 6: whitesur-gtk-theme — 6 subpackages across colour and opacity

WhiteSur has no size axis; its second axis is opacity (`normal`/`solid`), and it
spells blue explicitly. It emits Light/Dark rather than a base triple.

**Files:**
- Modify: `themes/whitesur-gtk-theme/whitesur-gtk-theme.spec`

- [ ] **Step 1: Set Release and `%install`**

Set `Release: 3%{?dist}` and replace `%install`:

```spec
%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# WhiteSur spells blue explicitly. -l omitted: verified no-op for the buildroot,
# including alongside --shell.
./install.sh -d %{buildroot}%{_datarootdir}/themes \
  -t blue -t red -t grey -N mojave --shell -i gnome
rm -rf %{buildroot}%{_datarootdir}/themes/*-hdpi
rm -rf %{buildroot}%{_datarootdir}/themes/*-xhdpi
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
find %{buildroot}%{_datarootdir}/themes -name COPYING -delete
```

- [ ] **Step 2: Add the hdpi gate to `%check`**

Append to the existing `%check`:

```bash
hdpi=$(find %{buildroot}%{_datadir}/themes -maxdepth 1 -type d \
  \( -name '*-hdpi' -o -name '*-xhdpi' \) | wc -l)
[ "$hdpi" -eq 0 ] || { echo "dpi gate FAIL: $hdpi hdpi dir(s) remain"; exit 1; }
echo "dpi gate: OK"
```

- [ ] **Step 3: Add subpackages and `%files` (names verified by a real build)**

```spec
%package blue
Summary:        WhiteSur GTK theme, blue accent
%description blue
Blue accent, translucent panel. Ships light and dark variants.

%package blue-solid
Summary:        WhiteSur GTK theme, blue accent, opaque
%description blue-solid
Blue accent, opaque panel. Ships light and dark variants.

%package red
Summary:        WhiteSur GTK theme, red accent
%description red
Red accent, translucent panel. Ships light and dark variants.

%package red-solid
Summary:        WhiteSur GTK theme, red accent, opaque
%description red-solid
Red accent, opaque panel. Ships light and dark variants.

%package grey
Summary:        WhiteSur GTK theme, grey accent
%description grey
Grey accent, translucent panel. Ships light and dark variants.

%package grey-solid
Summary:        WhiteSur GTK theme, grey accent, opaque
%description grey-solid
Grey accent, opaque panel. Ships light and dark variants.
```

```spec
%files
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-blue
%{_datarootdir}/themes/WhiteSur-Dark-blue

%files blue-solid
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-solid-blue
%{_datarootdir}/themes/WhiteSur-Dark-solid-blue

%files red
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-red
%{_datarootdir}/themes/WhiteSur-Dark-red

%files red-solid
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-solid-red
%{_datarootdir}/themes/WhiteSur-Dark-solid-red

%files grey
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-grey
%{_datarootdir}/themes/WhiteSur-Dark-grey

%files grey-solid
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-solid-grey
%{_datarootdir}/themes/WhiteSur-Dark-solid-grey
```

Add the changelog entry:

```spec
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-3
- Split into colour/opacity packages (blue, red, grey x normal, solid). WhiteSur
  has no size axis; its second axis is panel opacity.
- Drop -hdpi/-xhdpi (xfwm4-only, unusable on GNOME); gated in %%check.
- Strip cinnamon/xfwm4/plank/unity; keep gtk-2.0 and metacity-1.
- Drop -l/--libadwaita: verified byte-identical buildroot without it, including
  alongside --shell.
```

- [ ] **Step 4: Build, lint, commit**

```bash
cd /home/ekthor/Projects/rpm-specs
cp themes/whitesur-gtk-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R themes/whitesur-gtk-theme/whitesur-gtk-theme.spec
rpmbuild -bs themes/whitesur-gtk-theme/whitesur-gtk-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/whitesur-gtk-theme-20260707-3.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'GTK4 CSS parse|node-gate|strip gate|dpi gate' /var/lib/mock/fedora-44-x86_64/result/build.log
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
rpmlint -c rpmlint.toml /var/lib/mock/fedora-44-x86_64/result/*.noarch.rpm 2>&1 | tail -2
git add themes/whitesur-gtk-theme/
git commit -m "whitesur-gtk-theme: split into colour/opacity packages

6 packages (blue, red, grey x normal, solid). WhiteSur has no size axis; its
second axis is panel opacity. DPI variants dropped, non-GNOME payload stripped.

Verified: mock exit 0, all gates OK, both lint gates 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: `mock exit=0`, all four gates OK, `7` noarch RPMs, both lint gates
`0 errors, 0 warnings`.

---

### Task 7: qogir-icon-theme — one colour package

Like the GTK theme, Qogir's icon `-t` is distro branding, so one package ships.
Icon themes have no `gtk-4.0` CSS and no `gnome-shell.css`, so their `%check`
gates on `index.theme` and dangling symlinks instead.

**Files:**
- Modify: `icons/qogir-icon-theme/qogir-icon-theme.spec`

- [ ] **Step 1: Set Release and `%install`**

Set `Release: 5%{?dist}` and replace `%install`:

```spec
%install
mkdir -p %{buildroot}%{_datarootdir}/icons
# -t selects distro branding, not accent colour, so only the default ships.
./install.sh --theme default --color all --dest "%{buildroot}%{_datarootdir}/icons"
```

- [ ] **Step 2: Add `%check`**

Insert before `%files`:

```spec
%check
n=0
for d in %{buildroot}%{_datadir}/icons/*/; do
  n=$((n+1))
  [ -f "$d/index.theme" ] || { echo "FAIL: no index.theme in $d"; exit 1; }
done
[ "$n" -gt 0 ] || { echo "FAIL: no icon themes installed"; exit 1; }
echo "index.theme gate: OK ($n themes)"
dangling=$(find %{buildroot}%{_datadir}/icons -xtype l | wc -l)
[ "$dangling" -eq 0 ] || {
  echo "FAIL: $dangling dangling symlink(s):"
  find %{buildroot}%{_datadir}/icons -xtype l -printf '  %p -> %l\n' | head -20
  exit 1
}
echo "dangling-symlink gate: OK (0 across $n themes)"
```

- [ ] **Step 3: Write `%files` (names verified by a real build)**

```spec
%files
%license COPYING
%{_datarootdir}/icons/Qogir
%{_datarootdir}/icons/Qogir-Light
%{_datarootdir}/icons/Qogir-Dark
```

Add the changelog entry:

```spec
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250215-5
- No colour split: Qogir's -t selects distro branding (default|manjaro|ubuntu),
  not accent colour, so only the default variant ships.
- Add a %%check: index.theme gate and a zero-dangling-symlink gate.
```

- [ ] **Step 4: Build, lint, commit**

```bash
cd /home/ekthor/Projects/rpm-specs
spectool -g -R icons/qogir-icon-theme/qogir-icon-theme.spec
rpmbuild -bs icons/qogir-icon-theme/qogir-icon-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/qogir-icon-theme-20250215-5.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'index.theme gate|dangling-symlink gate' /var/lib/mock/fedora-44-x86_64/result/build.log
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
git add icons/qogir-icon-theme/
git commit -m "qogir-icon-theme: add %check, ship default branding only

Qogir's -t selects distro branding, not accent colour, so no colour split
applies. Adds an index.theme gate and a zero-dangling-symlink gate.

Verified: mock exit 0, both gates OK, spec lint 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: `mock exit=0`, `index.theme gate: OK (3 themes)`,
`dangling-symlink gate: OK (0 across 3 themes)`, spec lint `0 errors, 0 warnings`.

---

### Task 8: whitesur-icon-theme — 3 colour packages

Already carries `fix-dangling-symlinks.patch` and the two `%check` gates from
the committed work; this task only constrains colours and splits packages.

**Files:**
- Modify: `icons/whitesur-icon-theme/whitesur-icon-theme.spec`

- [ ] **Step 1: Set Release and `%install`**

Set `Release: 4%{?dist}` and replace the `install.sh` line in `%install`:

```spec
./install.sh --theme default --theme red --theme grey \
  --alternative --dest "%{buildroot}%{_datarootdir}/icons"
```

- [ ] **Step 2: Add subpackages**

```spec
%package blue
Summary:        WhiteSur icon theme, blue accent
%description blue
Blue accent. Ships light, dark and auto variants.

%package red
Summary:        WhiteSur icon theme, red accent
%description red
Red accent. Ships light, dark and auto variants.

%package grey
Summary:        WhiteSur icon theme, grey accent
%description grey
Grey accent. Ships light, dark and auto variants.
```

- [ ] **Step 3: Write `%files` (names verified by a real build)**

```spec
%files
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/icons/WhiteSur
%{_datarootdir}/icons/WhiteSur-light
%{_datarootdir}/icons/WhiteSur-dark

%files red
%license COPYING
%{_datarootdir}/icons/WhiteSur-red
%{_datarootdir}/icons/WhiteSur-red-light
%{_datarootdir}/icons/WhiteSur-red-dark

%files grey
%license COPYING
%{_datarootdir}/icons/WhiteSur-grey
%{_datarootdir}/icons/WhiteSur-grey-light
%{_datarootdir}/icons/WhiteSur-grey-dark
```

Add the changelog entry:

```spec
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-4
- Split into colour packages (blue, red, grey). Blue is upstream's "default"
  accent; packages are named for the colour.
```

- [ ] **Step 4: Build, lint, commit**

```bash
cd /home/ekthor/Projects/rpm-specs
cp icons/whitesur-icon-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R icons/whitesur-icon-theme/whitesur-icon-theme.spec
rpmbuild -bs icons/whitesur-icon-theme/whitesur-icon-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/whitesur-icon-theme-20260707-4.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'index.theme gate|dangling-symlink gate' /var/lib/mock/fedora-44-x86_64/result/build.log
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
git add icons/whitesur-icon-theme/
git commit -m "whitesur-icon-theme: split into colour packages

3 colour packages (blue, red, grey). Blue is upstream's 'default' accent;
packages are named for the colour.

Verified: mock exit 0, index.theme and dangling-symlink gates OK, spec lint 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: `mock exit=0`, `index.theme gate: OK (9 themes)`,
`dangling-symlink gate: OK (0 across 9 themes)`, spec lint `0 errors, 0 warnings`.

---

### Task 9: tela-icon-theme — 3 colour packages

Tela takes colours as **positional arguments**, not flags. It has no `-t`.

**Files:**
- Modify: `icons/tela-icon-theme/tela-icon-theme.spec`

- [ ] **Step 1: Set Release and `%install`**

Set `Release: 4%{?dist}` and replace the `install.sh` line:

```spec
# Tela takes colours as positional arguments; it has no -t flag.
./install.sh -d "%{buildroot}%{_datarootdir}/icons" blue red grey
```

- [ ] **Step 2: Add subpackages**

```spec
%package blue
Summary:        Tela icon theme, blue accent
%description blue
Blue accent. Ships light, dark and auto variants.

%package red
Summary:        Tela icon theme, red accent
%description red
Red accent. Ships light, dark and auto variants.

%package grey
Summary:        Tela icon theme, grey accent
%description grey
Grey accent. Ships light, dark and auto variants.
```

- [ ] **Step 3: Write `%files` (names verified by a real build)**

```spec
%files
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/icons/Tela-blue
%{_datarootdir}/icons/Tela-blue-light
%{_datarootdir}/icons/Tela-blue-dark

%files red
%license COPYING
%{_datarootdir}/icons/Tela-red
%{_datarootdir}/icons/Tela-red-light
%{_datarootdir}/icons/Tela-red-dark

%files grey
%license COPYING
%{_datarootdir}/icons/Tela-grey
%{_datarootdir}/icons/Tela-grey-light
%{_datarootdir}/icons/Tela-grey-dark
```

Add the changelog entry:

```spec
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-4
- Split into colour packages (blue, red, grey). Tela takes colours as positional
  arguments, not flags.
```

- [ ] **Step 4: Build, lint, commit**

```bash
cd /home/ekthor/Projects/rpm-specs
cp icons/tela-icon-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R icons/tela-icon-theme/tela-icon-theme.spec
rpmbuild -bs icons/tela-icon-theme/tela-icon-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/tela-icon-theme-20260707-4.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'index.theme gate|dangling-symlink gate' /var/lib/mock/fedora-44-x86_64/result/build.log
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
git add icons/tela-icon-theme/
git commit -m "tela-icon-theme: split into colour packages

3 colour packages (blue, red, grey). Tela takes colours as positional
arguments, not flags.

Verified: mock exit 0, index.theme and dangling-symlink gates OK, spec lint 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: `mock exit=0`, `index.theme gate: OK (9 themes)`,
`dangling-symlink gate: OK (0 across 9 themes)`, spec lint `0 errors, 0 warnings`.

---

### Task 10: tela-circle-icon-theme — 3 colour packages

Tela-circle's `-c` means **circular folder version and takes no argument**; the
colour that follows it is positional. The current spec's `-c standard` therefore
means "circular, colour standard", not "colour=standard".

**Files:**
- Modify: `icons/tela-circle-icon-theme/tela-circle-icon-theme.spec`

- [ ] **Step 1: Set Release and `%install`**

Set `Release: 4%{?dist}` and replace the `install.sh` line:

```spec
# -c enables the circular folder version and takes no argument; the colours
# that follow are positional.
./install.sh -d "%{buildroot}%{_datarootdir}/icons" -c blue red grey
```

- [ ] **Step 2: Add subpackages**

```spec
%package blue
Summary:        Tela-circle icon theme, blue accent
%description blue
Blue accent, circular folders. Ships light, dark and auto variants.

%package red
Summary:        Tela-circle icon theme, red accent
%description red
Red accent, circular folders. Ships light, dark and auto variants.

%package grey
Summary:        Tela-circle icon theme, grey accent
%description grey
Grey accent, circular folders. Ships light, dark and auto variants.
```

- [ ] **Step 3: Write `%files` (names verified by a real build)**

```spec
%files
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/icons/Tela-circle-blue
%{_datarootdir}/icons/Tela-circle-blue-light
%{_datarootdir}/icons/Tela-circle-blue-dark

%files red
%license COPYING
%{_datarootdir}/icons/Tela-circle-red
%{_datarootdir}/icons/Tela-circle-red-light
%{_datarootdir}/icons/Tela-circle-red-dark

%files grey
%license COPYING
%{_datarootdir}/icons/Tela-circle-grey
%{_datarootdir}/icons/Tela-circle-grey-light
%{_datarootdir}/icons/Tela-circle-grey-dark
```

Add the changelog entry:

```spec
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-4
- Split into colour packages (blue, red, grey). Note -c enables the circular
  folder version and takes no argument; colours are positional, so the previous
  "-c standard" meant "circular, colour standard".
```

- [ ] **Step 4: Build, lint, commit**

```bash
cd /home/ekthor/Projects/rpm-specs
cp icons/tela-circle-icon-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R icons/tela-circle-icon-theme/tela-circle-icon-theme.spec
rpmbuild -bs icons/tela-circle-icon-theme/tela-circle-icon-theme.spec
mock -r fedora-44-x86_64 --rebuild ~/rpmbuild/SRPMS/tela-circle-icon-theme-20260707-4.fc44.src.rpm
echo "mock exit=$?"
rtk proxy grep -E 'index.theme gate|dangling-symlink gate' /var/lib/mock/fedora-44-x86_64/result/build.log
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
git add icons/tela-circle-icon-theme/
git commit -m "tela-circle-icon-theme: split into colour packages

3 colour packages (blue, red, grey). -c enables circular folders and takes no
argument; colours are positional, so the previous '-c standard' meant
'circular, colour standard'.

Verified: mock exit 0, index.theme and dangling-symlink gates OK, spec lint 0/0.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

Expected: `mock exit=0`, `index.theme gate: OK (9 themes)`,
`dangling-symlink gate: OK (0 across 9 themes)`, spec lint `0 errors, 0 warnings`.

---

### Task 11: Sync README and run the full-repo gate

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-07-19-theme-packaging-design.md` (status)

- [ ] **Step 1: Update the specs table**

For each of the 9 theme/icon rows, set the new `Version-Release` and describe
what it now ships — the colour packages by name, not "a theme". Rename the three
renamed rows. Confirm the current values first:

```bash
cd /home/ekthor/Projects/rpm-specs
for s in */*/*.spec; do
  printf '%-46s ' "$s"
  rtk proxy grep -hE '^(Name|Version|Release):' "$s" | tr -s ' ' | tr '\n' ' '
  echo
done
```

- [ ] **Step 2: Update the per-spec build sections and quick-reference table**

Every build command in README must use the new `<category>/<pkg>/<pkg>.spec`
paths. The "vinceliuice GTK themes" section must state that patches are staged
one spec at a time because basenames collide. The quick-reference table gains
the three `fix-dangling-symlinks.patch` local sources.

- [ ] **Step 3: Update the Linting section**

The gate command is now `rpmlint -c rpmlint.toml */*/*.spec`. Update the
`%check` count: 5 GTK themes with 4 gates each, 4 icon themes with 2 gates each.
Note the new `no-documentation` filter and why it exists.

- [ ] **Step 4: Mark the design spec implemented**

In section 8 of the design spec, note that implementation is complete and record
the actual package count produced.

- [ ] **Step 5: Verify every claim in the README against reality**

```bash
cd /home/ekthor/Projects/rpm-specs
find themes icons apps kernel -name '*.spec' | sort
rpmlint -c rpmlint.toml */*/*.spec 2>&1 | tail -2
copr-cli list-packages wdm | rtk proxy grep '"name"' | sort
```
Expected: 14 specs; lint `0 errors, 0 warnings`; the COPR list contains
`fluent-gtk-theme`, `orchis-gtk-theme`, `qogir-gtk-theme` and none of
`fluent-gtk-theme-compact`, `orchis-theme`, `qogir-theme`.

- [ ] **Step 6: Commit**

```bash
cd /home/ekthor/Projects/rpm-specs
git add README.md docs/
git commit -m "README: sync with category layout and colour packages

Paths move to <category>/<pkg>/<pkg>.spec and the lint gate becomes
*/*/*.spec. Specs table records the new Version-Release and the colour
packages each source now produces. Notes that patches must be staged one spec
at a time because basenames collide.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Rollback

Every task is one commit. To undo a package conversion, `git revert` its commit
and rebuild. COPR package deletions in Tasks 2, 4 and 5 are **not** reverted by
git: recreate the package by building the old spec, or accept the rename.

## Deferred

Not in scope, recorded so they are not lost:

- Pushing to COPR and observing repodata generation, mirror sync and web UI at
  44 packages. Local `createrepo_c` measured 506 KB repodata for 11 RPMs
  (3.75 bytes per filesystem entry) and `dnf makecache` at 0.02 s, but COPR's
  own pipeline is unobserved.
- Packaging `adw-gtk3` 6.5. Fedora ships 6.4-3.fc44 while upstream 6.5 is
  titled "Release for GNOME 50" — the clearest gap found in the research
  appendix.
- Packaging MoreWaita, which ships `meson.build` and `PACKAGING.md` and is not
  in Fedora.
- Reporting the dangling-symlink defects upstream. The downstream patches fix
  the symptom in this COPR only.
