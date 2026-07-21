# rpm-specs

RPM spec files for Fedora 44 packages I maintain in the COPR
[raro28/wdm](https://copr.fedorainfracloud.org/coprs/raro28/wdm/).
Each subdirectory is one source package.

## Specs in this repo

| Spec | Current build | What it ships |
|---|---|---|
| themes/colloid-gtk-theme | `20250731-7` | GTK theme ([vinceliuice/Colloid-gtk-theme](https://github.com/vinceliuice/Colloid-gtk-theme)), GNOME 50 patches; ships blue, blue-compact, red, red-compact, grey, grey-compact |
| themes/fluent-gtk-theme | `20250417-9` | GTK theme ([vinceliuice/Fluent-gtk-theme](https://github.com/vinceliuice/Fluent-gtk-theme)), GNOME 50 patches; ships blue, blue-compact, red, red-compact, grey, grey-compact |
| apps/gnome-shell-extension-per-monitor-wallpaper | `2.2.1-1` | GNOME Shell extension, per-monitor wallpapers; reader-only (editing GUI is `mural`) ([raro28/per-monitor-wallpaper](https://github.com/raro28/per-monitor-wallpaper)) |
| apps/llama.cpp | `0^b10068-1` | LLM inference, CPU engine + embedded web UI; GPU via `-vulkan`/`-rocm` backend subpackages ([ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)) |
| apps/looking-glass-client | `7.0.0-14` | Looking Glass B7 client + SELinux subpackage ([gnif/LookingGlass](https://github.com/gnif/LookingGlass)) |
| kernel/looking-glass-kvmfr-kmod | `0.0.12-7` | akmod for the `kvmfr` kernel module ([gnif/LookingGlass](https://github.com/gnif/LookingGlass)) — see [its README](kernel/looking-glass-kvmfr-kmod/README.md) |
| apps/mural | `1.0.2-1` | Per-monitor wallpaper editor, standalone GTK4/libadwaita app ([raro28/mural](https://github.com/raro28/mural)) |
| themes/orchis-gtk-theme | `20260707-3` | GTK theme ([vinceliuice/Orchis-theme](https://github.com/vinceliuice/Orchis-theme)), GNOME 50 patches; ships blue, blue-compact, red, red-compact, grey, grey-compact |
| themes/qogir-gtk-theme | `20250817-7` | GTK theme ([vinceliuice/Qogir-theme](https://github.com/vinceliuice/Qogir-theme)), GNOME 50 patches; single package, no color subpackages (`-t` selects distro branding, not an accent) |
| icons/qogir-icon-theme | `20250215-5` | Icon theme ([vinceliuice/Qogir-icon-theme](https://github.com/vinceliuice/Qogir-icon-theme)); single package, no color subpackages (same reason) |
| icons/tela-circle-icon-theme | `20260707-4` | Icon theme ([vinceliuice/Tela-circle-icon-theme](https://github.com/vinceliuice/Tela-circle-icon-theme)); ships blue, red, grey |
| icons/tela-icon-theme | `20260707-4` | Icon theme ([vinceliuice/Tela-icon-theme](https://github.com/vinceliuice/Tela-icon-theme)); ships blue, red, grey |
| themes/whitesur-gtk-theme | `20260707-3` | GTK theme ([vinceliuice/WhiteSur-gtk-theme](https://github.com/vinceliuice/WhiteSur-gtk-theme)), GNOME 50 patches; ships blue, blue-solid, red, red-solid, grey, grey-solid |
| icons/whitesur-icon-theme | `20260707-4` | Icon theme ([vinceliuice/WhiteSur-icon-theme](https://github.com/vinceliuice/WhiteSur-icon-theme)); ships blue, red, grey |

## Host setup (once)

Install the build toolchain and prepare `~/rpmbuild`:

```bash
sudo dnf install rpm-build rpmdevtools mock
sudo usermod -aG mock $USER
# log out / back in (or `newgrp mock`) so the mock group is active
rpmdev-setuptree            # creates ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
```

- `rpm-build`  → `rpmbuild`
- `rpmdevtools` → `spectool` (fetches `Source:` URLs), `rpmdev-setuptree`
- `mock` → clean fedora-44-x86_64 chroot builder

No spec in this repo needs additional BuildRequires on the host — mock auto-installs them inside the chroot from Fedora's main repos.

## Common build workflow

Same four steps for every spec. From the repo root:

```bash
SPEC=<category>/<spec-dir>/<spec-name>.spec     # e.g. themes/qogir-gtk-theme/qogir-gtk-theme.spec

# 1. (only if the spec has LOCAL source files) copy them into SOURCES
#    See the per-spec table below — most have none.

# 2. Fetch all URL-based Sources into ~/rpmbuild/SOURCES/
spectool -g -R "$SPEC"

# 3. Build the SRPM
rpmbuild -bs "$SPEC"

# 4. Build binary RPMs in a clean F44 chroot
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/<srpm-basename>.fc44.src.rpm
# Results: /var/lib/mock/fedora-44-x86_64/result/*.rpm

# 5. (optional) install locally
sudo dnf install /var/lib/mock/fedora-44-x86_64/result/*.rpm
```

`mock` reads each `Source:` from `~/rpmbuild/SOURCES/`. URLs are NOT fetched at mock time — `spectool` is what populates the cache.

## Per-spec build instructions

### Pure-upstream specs (no local sources)

`Source0` (GitHub tarball) only; canonical 4 steps, nothing to copy:

- `apps/gnome-shell-extension-per-monitor-wallpaper`
- `apps/mural`
- `icons/qogir-icon-theme` (single package; no color subpackages, no patches — see below)

```bash
spectool -g -R icons/qogir-icon-theme/qogir-icon-theme.spec
rpmbuild -bs icons/qogir-icon-theme/qogir-icon-theme.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/qogir-icon-theme-20250215-5.fc44.src.rpm
```

`gnome-shell-extension-per-monitor-wallpaper` installs system-wide; each user enables it with `gnome-extensions enable per-monitor-wallpaper@ekthor`. Requires GNOME Shell 50.x (versioned `Requires`). Authored in TypeScript, built by CI into the release tarball (Source0); the RPM compiles nothing and has no `BuildRequires`.

### mural

Standalone GTK4/libadwaita editor for the config the `gnome-shell-extension-per-monitor-wallpaper` reader paints from. Authored in TypeScript, built by CI into the release tarball (`Source0`, which also bundles the man page and `LICENSE`); the RPM compiles nothing and has no local sources. Carries a `%check` (`desktop-file-validate` + `appstreamcli validate`; `BuildRequires: desktop-file-utils appstream`, auto-installed in the chroot). Runtime `Requires`: `gjs`, `gtk4`, `libadwaita`, `glycin-libs`, `glycin-gtk4-libs`, `glycin-loaders`, `hicolor-icon-theme`.

```bash
spectool -g -R apps/mural/mural.spec
rpmbuild -bs apps/mural/mural.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/mural-1.0.2-1.fc44.src.rpm
```

### vinceliuice GTK themes (GNOME 50 patches, color subpackages)

`themes/colloid-gtk-theme`, `themes/fluent-gtk-theme`, `themes/orchis-gtk-theme`, `themes/qogir-gtk-theme`, `themes/whitesur-gtk-theme`. Each carries downstream GNOME 50 patches (local files, stage in `SOURCES/`) and a `%check` (`BuildRequires: gtk4 python3-gobject-base`, auto-installed in the chroot) — see Linting below for the gate counts (4, except fluent-gtk-theme's 3). Four of the five split into color subpackages (`colloid`/`fluent`/`orchis`: blue, blue-compact, red, red-compact, grey, grey-compact; `whitesur-gtk`: blue, blue-solid, red, red-solid, grey, grey-solid); `qogir-gtk-theme` ships a single package — its `-t` flag selects distro branding, not an accent color.

| Spec | Patches |
|---|---|
| themes/colloid-gtk-theme | gnome50-selectors, gnome50-appearance, fix-fsf-address |
| themes/fluent-gtk-theme | gnome50-selectors, gnome50-appearance, fix-shell-bg-position |
| themes/orchis-gtk-theme | gnome50-selectors, gnome50-appearance, fix-gtk4-define-color, fix-shell-bg-position |
| themes/qogir-gtk-theme | gnome50-selectors, gnome50-appearance |
| themes/whitesur-gtk-theme | gnome50-selectors, gnome50-appearance, fix-fsf-address, fix-shell-bg-position |

**Patch basenames collide across specs**: all 5 GTK themes above ship `gnome50-selectors.patch` and `gnome50-appearance.patch`; the 3 icon themes below ship `fix-dangling-symlinks.patch`. `~/rpmbuild/SOURCES/` is flat, so copying patches for more than one spec at a time silently overwrites and a later spec builds against an earlier spec's patch — it fails as a bogus "hunk FAILED", not as a staging error. **Stage and build one spec at a time.**

Example (`themes/qogir-gtk-theme`):

```bash
cp themes/qogir-gtk-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R themes/qogir-gtk-theme/qogir-gtk-theme.spec
rpmbuild -bs themes/qogir-gtk-theme/qogir-gtk-theme.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/qogir-gtk-theme-20250817-7.fc44.src.rpm
```

Patch reference:

- `gnome50-selectors.patch` — styles GNOME 50 login `.a11y-button` and notification `.message-list-clear-button` with the theme's own button styling (additive sibling selectors, inert on GNOME < 49).
- `gnome50-appearance.patch` — GNOME 50 native geometry: `.login-dialog-bottom-button-group` 32px/16px, `.message-list-clear-button` `border-radius: 999px`.
- `fix-fsf-address.patch` (colloid, whitesur) — replaces the outdated FSF postal address in the upstream `gnome-shell.css` GPL header with the canonical URL form (clears rpmlint `incorrect-fsf-address`).
- `fix-gtk4-define-color.patch` (orchis) — the libadwaita build emitted `@define-color theme_{,unfocused_}selected_bg_color var(--accent-bg-color)`, which GTK's `@define-color` rejects; references the defined `@accent_color` in the libadwaita case only (the GTK3 literal is untouched).
- `fix-shell-bg-position.patch` (fluent, orchis, whitesur) — the upstream `#panelActivities` rule sets `background-position: center center`, a keyword St's shell CSS engine cannot parse (logged at runtime as `Ignoring length property that isn't a number`); St drops it and falls back to `0 0`, so setting `0 0` explicitly is pixel-identical and silences the warning.

### vinceliuice icon themes with a patch (dangling-symlink fix)

`icons/tela-icon-theme`, `icons/tela-circle-icon-theme`, `icons/whitesur-icon-theme`. Each carries one local patch, `fix-dangling-symlinks.patch` (repoints upstream aliases that `install.sh` leaves broken), and a `%check` — see Linting below for the 2 gates. `tela`/`tela-circle` split into blue/red/grey; `whitesur-icon` also splits into blue/red/grey. Same one-spec-at-a-time staging rule as above (basename collides across these three).

```bash
cp icons/tela-icon-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R icons/tela-icon-theme/tela-icon-theme.spec
rpmbuild -bs icons/tela-icon-theme/tela-icon-theme.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/tela-icon-theme-20260707-4.fc44.src.rpm
```

### llama.cpp

No local sources, but two URL sources: `Source0` (the source tarball) and `Source1` (the prebuilt `llama-bNNNN-ui.tar.gz` web-UI bundle from the matching GitHub release, extracted into `tools/ui/dist` during `%prep` so the server embeds the SvelteKit UI without pulling in nodejs/npm at build time). `spectool -g -R` fetches both.

One SRPM builds three coexisting binary RPMs off the `GGML_BACKEND_DL` module layout (`-DGGML_VULKAN=ON -DGGML_HIP=ON` in a single pass):

- **`llama.cpp`** (base) — `llama-cli`, `llama-server` (with web UI), `llama-bench`, `llama-quantize` etc. plus the CPU backend (all x86-64 variants, runtime-dispatched). No GPU dependency; `Recommends: llama.cpp-vulkan` so a bare install stays GPU-accelerated.
- **`llama.cpp-vulkan`** — the `libggml-vulkan.so` dlopen module; `Recommends: mesa-vulkan-drivers` (RADV/ANV for AMD/Intel, NVIDIA proprietary). Portable across vendors.
- **`llama.cpp-rocm`** — the `libggml-hip.so` dlopen module built for `GPU_TARGETS=gfx1030` (RDNA2, RX 6800/6900 XT); auto-pulls rocBLAS/hipBLAS. The gfx1030 kernels compile ahead-of-time from the ISA string, so no GPU is needed to build (or in COPR).

ggml loads whichever backend modules are installed and enumerates all their devices; the backends coexist, and RPM's soname-based dep generation isolates each GPU stack to its own subpackage. The `-rocm` gfx target is a one-line `%global amdgpu_targets` macro.

```bash
spectool -g -R apps/llama.cpp/llama.cpp.spec
rpmbuild -bs apps/llama.cpp/llama.cpp.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/llama.cpp-0\^b10068-1.fc44.src.rpm
```

**Note the `\^` shell-escape** when typing the SRPM filename — `^` is the Fedora-standard post-release snapshot marker (upstream tags are `bNNNN` build numbers, no semver), and the literal caret appears in the filename.

To bump the upstream version, update `%global build_num` in the spec (one line). The current `bNNNN` tag is at <https://github.com/ggml-org/llama.cpp/releases>.

### looking-glass-client

Builds two installable RPMs: `looking-glass-client` and `looking-glass-client-selinux`. Mock also produces `looking-glass-client-debuginfo` and `looking-glass-client-debugsource` automatically (the spec doesn't suppress them); installing only the first two is the normal path.

**Local sources** to stage before `spectool`:

```
apps/looking-glass-client/10-looking-glass-client.conf
apps/looking-glass-client/looking-glass-client.desktop
apps/looking-glass-client/looking-glass-client.te
apps/looking-glass-client/looking-glass-client.fc
```

**Upstream tarball gotcha**: GitHub's tag-archive of `gnif/LookingGlass` does not recurse into git submodules. The spec declares `Source10..15` for each submodule (LGMP, PureSpice, cimgui, imgui, nanosvg, wayland-protocols) pinned to its gitlink SHA. `spectool` fetches all of them.

```bash
cp apps/looking-glass-client/{10-looking-glass-client.conf,looking-glass-client.desktop,looking-glass-client.te,looking-glass-client.fc} \
   ~/rpmbuild/SOURCES/
spectool -g -R apps/looking-glass-client/looking-glass-client.spec
rpmbuild -bs apps/looking-glass-client/looking-glass-client.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/looking-glass-client-7.0.0-14.fc44.src.rpm
```

To bump the upstream version, update `%global upstream_tag` in the spec and refresh the six submodule SHAs via:

```bash
git ls-tree <new-tag> repos/    # in a clone of gnif/LookingGlass
git ls-tree <cimgui_sha> imgui  # in a clone of cimgui/cimgui
```

### looking-glass-kvmfr-kmod

akmod for the `kvmfr` kernel module. Builds four RPMs:

- `akmod-kvmfr` (source-shipping)
- `kmod-kvmfr` (meta)
- `kvmfr-kmod-common` (modprobe.d + udev + modules-load.d + LICENSE)
- `kvmfr-kmod-selinux` (targeted SELinux policy)

The `.ko` is **not** compiled at mock/COPR time — the akmods service rebuilds it on each user's machine against their installed kernel.

**Local sources** to stage before `spectool`:

```
kernel/looking-glass-kvmfr-kmod/kvmfr.conf
kernel/looking-glass-kvmfr-kmod/99-kvmfr.rules
kernel/looking-glass-kvmfr-kmod/kvmfr.te
kernel/looking-glass-kvmfr-kmod/kvmfr.fc
kernel/looking-glass-kvmfr-kmod/kvmfr-modules-load.conf
kernel/looking-glass-kvmfr-kmod/0001-add-module-description.patch
```

```bash
cp kernel/looking-glass-kvmfr-kmod/{kvmfr.conf,99-kvmfr.rules,kvmfr.te,kvmfr.fc,kvmfr-modules-load.conf,0001-add-module-description.patch} \
   ~/rpmbuild/SOURCES/
spectool -g -R kernel/looking-glass-kvmfr-kmod/looking-glass-kvmfr-kmod.spec
rpmbuild -bs kernel/looking-glass-kvmfr-kmod/looking-glass-kvmfr-kmod.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/looking-glass-kvmfr-kmod-0.0.12-7.fc44.src.rpm
```

After installing, `/dev/kvmfr0` needs **two manual host configuration steps** (libvirt cgroup ACL + VM XML cutover) the package cannot do for you — see [kernel/looking-glass-kvmfr-kmod/README.md](kernel/looking-glass-kvmfr-kmod/README.md) for the full setup, verification, rollback, and SELinux details.

## Quick reference: which specs need local sources?

| Spec | Local sources? | URL sources? |
|---|---|---|
| icons/qogir-icon-theme | No | Source0 only |
| apps/gnome-shell-extension-per-monitor-wallpaper | No | Source0 only |
| apps/llama.cpp | No | Source0 + Source1 (web-UI bundle) |
| apps/mural | No | Source0 only |
| 5 vinceliuice GTK themes (`themes/`) | **Yes** — 2–4 patches | Source0 only |
| icons/tela-icon-theme, icons/tela-circle-icon-theme, icons/whitesur-icon-theme | **Yes** — 1 patch (fix-dangling-symlinks.patch) | Source0 only |
| apps/looking-glass-client | **Yes** — 4 files | Source0 + 6 submodule URLs |
| kernel/looking-glass-kvmfr-kmod | **Yes** — 5 files + 1 patch | Source0 only |

When sources drift between the spec directory and `~/rpmbuild/SOURCES/`, the build silently uses the stale copies. Re-copying before `rpmbuild -bs` is cheap insurance.

## Linting

All specs are kept at **zero rpmlint warnings**. Run from the repo root with the
bundled config:

```bash
sudo dnf install rpmlint        # once
rpmlint -c rpmlint.toml */*/*.spec
# expect: 0 errors, 0 warnings, 0 badness
```

`-c rpmlint.toml` adds repo-local filters on top of Fedora's defaults, including
these added in the theme/icon color-subpackage split:

- `no-%check-section` — suppressed for the 2 specs with no test to run (the
  kvmfr akmod, the GJS extension). All 9 vinceliuice theme/icon specs, plus
  llama.cpp, looking-glass-client, and mural, carry a real `%check`.
- `spelling-error` — this branch adds `nana`/`materia` to the filtered word
  list: `orchis-gtk-theme`'s `%description` credits the upstream projects it's
  based on (`nana-4`, `materia-theme`) — proper nouns, not misspellings.
- `no-documentation` for the vinceliuice theme family (`colloid|fluent|orchis|
  qogir|tela|tela-circle|whitesur` `-gtk|icon-theme`) — the color/size
  subpackages ship `%license` only (in `tela-circle`'s case, not even that);
  rpmlint's documentation check doesn't accept `%license` as satisfying it.
- `dangling-relative-symlink` for `qogir-icon-theme` and `whitesur-icon-theme` —
  both alias whole `-light`/`-dark`/`Light`/`Dark` directories via directory
  symlinks; rpmlint doesn't resolve through the intermediate directory symlink
  to check the real target. Verified 0 broken on disk (`find -xtype l` over the
  extracted tree) for every flagged path.
- `explicit-lib-dependency (libadwaita|glycin-libs|glycin-gtk4-libs)` — mural is a
  noarch GJS app, so RPM generates no automatic dependencies; its runtime
  GObject-Introspection deps must be explicit, and none of these packages expose a
  `typelib()` provide to depend on instead. False positive for this package.

The `%check` gates: four of the 5 GTK themes (colloid, orchis, qogir-gtk,
whitesur-gtk) run 4 — GTK4 CSS parse through the real engine
(`GtkCssProvider`), a GNOME 50 shell-selector node-gate, a component-strip gate,
and a DPI-directory gate. `fluent-gtk-theme` runs 3: it has no DPI axis (no
`-hdpi`/`-xhdpi` output), so no DPI gate. The 4 icon themes (qogir-icon, tela, tela-circle,
whitesur-icon) each run 2 — an `index.theme`-presence gate and a
zero-dangling-symlink gate. Every other warning class is fixed in the specs
(`%setup -q`/`%autosetup`, an explicit `%build`, `%%`-escaped `%changelog`
macros), so a plain `rpmlint */*/*.spec` only surfaces the filtered
`no-%check-section` (2 specs).

## COPR

The `raro28/wdm` COPR builds these from SRPMs uploaded via `copr-cli`, or via the Custom method pulling from this repo. COPR's chroot matches `mock -r fedora-44-x86_64` exactly — anything that builds locally builds there.

## Repo layout

```
.
├── README.md                              # this file
├── rpmlint.toml                           # repo-local rpmlint filter (see Linting)
├── themes/                                # GTK themes (colloid, fluent, orchis, qogir, whitesur)
│   └── <spec-dir>/
├── icons/                                 # icon themes (qogir, tela, tela-circle, whitesur)
│   └── <spec-dir>/
├── apps/                                  # standalone apps (mural, per-monitor-wallpaper,
│   └── <spec-dir>/                        # looking-glass-client, llama.cpp)
├── kernel/                                # kernel modules (looking-glass-kvmfr-kmod)
│   └── <spec-dir>/
│       ├── <spec-name>.spec
│       ├── README.md                      # only where extra runtime/cutover docs apply
│       └── [local source files referenced as SourceN]
└── ...
```

Each spec directory (`<category>/<spec-dir>/`) is self-contained: the spec plus the local source files it references.
