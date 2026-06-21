# rpm-specs

RPM spec files for Fedora 44 packages I maintain in the COPR
[raro28/wdm](https://copr.fedorainfracloud.org/coprs/raro28/wdm/).
Each subdirectory is one source package.

## Specs in this repo

| Spec | Current build | What it ships |
|---|---|---|
| colloid-gtk-theme | `20250731-5` | GTK theme (vinceliuice), GNOME 50 patches |
| fluent-gtk-theme-compact | `20250417-6` | GTK theme (vinceliuice), GNOME 50 patches |
| gnome-shell-extension-per-monitor-wallpaper | `1.0.1-1` | GNOME Shell extension, per-monitor wallpapers (raro28) |
| llama.cpp | `0^b9544-1` | LLM inference, Vulkan backend + embedded web UI (ggml-org/llama.cpp) |
| looking-glass-client | `7.0.0-14` | Looking Glass B7 client + SELinux subpackage |
| looking-glass-kvmfr-kmod | `0.0.12-7` | akmod for the `kvmfr` kernel module — see [its README](looking-glass-kvmfr-kmod/README.md) |
| orchis-theme | `20250425-5` | GTK theme (vinceliuice), GNOME 50 patches |
| qogir-icon-theme | `20250215-3` | Icon theme (vinceliuice) |
| qogir-theme | `20250817-5` | GTK theme (vinceliuice), GNOME 50 patches |
| tela-circle-icon-theme | `20250210-3` | Icon theme (vinceliuice) |
| tela-icon-theme | `20250210-1` | Icon theme (vinceliuice) |
| whitesur-gtk-theme | `20260606-2` | GTK theme (vinceliuice), GNOME 50 master snapshot + patches |
| whitesur-icon-theme | `20251227-1` | Icon theme (vinceliuice) |

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
SPEC=<spec-dir>/<spec-name>.spec     # e.g. qogir-theme/qogir-theme.spec

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

- `gnome-shell-extension-per-monitor-wallpaper`
- `qogir-icon-theme`
- `tela-circle-icon-theme`
- `tela-icon-theme`
- `whitesur-icon-theme`

```bash
spectool -g -R qogir-icon-theme/qogir-icon-theme.spec
rpmbuild -bs qogir-icon-theme/qogir-icon-theme.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/qogir-icon-theme-20250215-3.fc44.src.rpm
```

`gnome-shell-extension-per-monitor-wallpaper` installs system-wide; each user enables it with `gnome-extensions enable per-monitor-wallpaper@ekthor`. Requires GNOME Shell 50.x (versioned `Requires`); pure GJS, no `BuildRequires`.

### vinceliuice GTK themes (GNOME 50 patches)

`colloid-gtk-theme`, `fluent-gtk-theme-compact`, `orchis-theme`, `qogir-theme`, `whitesur-gtk-theme`. Each carries downstream GNOME 50 patches (local files, stage in `SOURCES/`) and a `%check` (GTK 4 CSS engine parse via `GtkCssProvider` + shell selector node-gate; `BuildRequires: gtk4 python3-gobject-base`, auto-installed in the chroot).

| Spec | Patches |
|---|---|
| colloid-gtk-theme | gnome50-selectors, gnome50-appearance, fix-fsf-address |
| fluent-gtk-theme-compact | gnome50-selectors, gnome50-appearance |
| orchis-theme | gnome50-selectors, gnome50-appearance, fix-gtk4-define-color |
| qogir-theme | gnome50-selectors, gnome50-appearance |
| whitesur-gtk-theme | gnome50-selectors, gnome50-appearance, fix-fsf-address |

Stage the patches with the glob, then build. Example (`qogir-theme`):

```bash
cp qogir-theme/*.patch ~/rpmbuild/SOURCES/
spectool -g -R qogir-theme/qogir-theme.spec
rpmbuild -bs qogir-theme/qogir-theme.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/qogir-theme-20250817-5.fc44.src.rpm
```

Patch reference:

- `gnome50-selectors.patch` — styles GNOME 50 login `.a11y-button` and notification `.message-list-clear-button` with the theme's own button styling (additive sibling selectors, inert on GNOME < 49).
- `gnome50-appearance.patch` — GNOME 50 native geometry: `.login-dialog-bottom-button-group` 32px/16px, `.message-list-clear-button` `border-radius: 999px`.
- `fix-fsf-address.patch` (colloid, whitesur) — replaces the outdated FSF postal address in the upstream `gnome-shell.css` GPL header with the canonical URL form (clears rpmlint `incorrect-fsf-address`).
- `fix-gtk4-define-color.patch` (orchis) — the libadwaita build emitted `@define-color theme_{,unfocused_}selected_bg_color var(--accent-bg-color)`, which GTK's `@define-color` rejects; references the defined `@accent_color` in the libadwaita case only (the GTK3 literal is untouched).

`whitesur-gtk-theme` additionally builds from a pinned `master` snapshot (`%global commit`) rather than the last tag (`20250724`, predates GNOME 49/50), date-versioned `20260606` so a future upstream `YYYYMMDD` tag supersedes it. Advance via `%global commit`.

### llama.cpp

No local sources, but two URL sources: `Source0` (the source tarball) and `Source1` (the prebuilt `llama-bNNNN-ui.tar.gz` web-UI bundle from the matching GitHub release, extracted into `tools/ui/dist` during `%prep` so the server embeds the SvelteKit UI without pulling in nodejs/npm at build time). `spectool -g -R` fetches both. Ships `llama-cli`, `llama-server` (with the web UI), `llama-bench`, `llama-quantize` etc. with the Vulkan backend enabled. Runtime needs a Vulkan ICD (`mesa-vulkan-drivers` for AMD/Intel; NVIDIA's proprietary driver provides one).

```bash
spectool -g -R llama.cpp/llama.cpp.spec
rpmbuild -bs llama.cpp/llama.cpp.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/llama.cpp-0\^b9544-1.fc44.src.rpm
```

**Note the `\^` shell-escape** when typing the SRPM filename — `^` is the Fedora-standard post-release snapshot marker (upstream tags are `bNNNN` build numbers, no semver), and the literal caret appears in the filename.

To bump the upstream version, update `%global build_num` in the spec (one line). The current `bNNNN` tag is at <https://github.com/ggml-org/llama.cpp/releases>.

### looking-glass-client

Builds two installable RPMs: `looking-glass-client` and `looking-glass-client-selinux`. Mock also produces `looking-glass-client-debuginfo` and `looking-glass-client-debugsource` automatically (the spec doesn't suppress them); installing only the first two is the normal path.

**Local sources** to stage before `spectool`:

```
looking-glass-client/10-looking-glass-client.conf
looking-glass-client/looking-glass-client.desktop
looking-glass-client/looking-glass-client.te
looking-glass-client/looking-glass-client.fc
```

**Upstream tarball gotcha**: GitHub's tag-archive of `gnif/LookingGlass` does not recurse into git submodules. The spec declares `Source10..15` for each submodule (LGMP, PureSpice, cimgui, imgui, nanosvg, wayland-protocols) pinned to its gitlink SHA. `spectool` fetches all of them.

```bash
cp looking-glass-client/{10-looking-glass-client.conf,looking-glass-client.desktop,looking-glass-client.te,looking-glass-client.fc} \
   ~/rpmbuild/SOURCES/
spectool -g -R looking-glass-client/looking-glass-client.spec
rpmbuild -bs looking-glass-client/looking-glass-client.spec
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
looking-glass-kvmfr-kmod/kvmfr.conf
looking-glass-kvmfr-kmod/99-kvmfr.rules
looking-glass-kvmfr-kmod/kvmfr.te
looking-glass-kvmfr-kmod/kvmfr.fc
looking-glass-kvmfr-kmod/kvmfr-modules-load.conf
looking-glass-kvmfr-kmod/0001-add-module-description.patch
```

```bash
cp looking-glass-kvmfr-kmod/{kvmfr.conf,99-kvmfr.rules,kvmfr.te,kvmfr.fc,kvmfr-modules-load.conf,0001-add-module-description.patch} \
   ~/rpmbuild/SOURCES/
spectool -g -R looking-glass-kvmfr-kmod/looking-glass-kvmfr-kmod.spec
rpmbuild -bs looking-glass-kvmfr-kmod/looking-glass-kvmfr-kmod.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/looking-glass-kvmfr-kmod-0.0.12-7.fc44.src.rpm
```

After installing, `/dev/kvmfr0` needs **two manual host configuration steps** (libvirt cgroup ACL + VM XML cutover) the package cannot do for you — see [looking-glass-kvmfr-kmod/README.md](looking-glass-kvmfr-kmod/README.md) for the full setup, verification, rollback, and SELinux details.

## Quick reference: which specs need local sources?

| Spec | Local sources? | URL sources? |
|---|---|---|
| 4 vinceliuice icon themes | No | Source0 only |
| gnome-shell-extension-per-monitor-wallpaper | No | Source0 only |
| llama.cpp | No | Source0 + Source1 (web-UI bundle) |
| 5 vinceliuice GTK themes | **Yes** — 2–3 patches | Source0 only |
| looking-glass-client | **Yes** — 4 files | Source0 + 6 submodule URLs |
| looking-glass-kvmfr-kmod | **Yes** — 5 files + 1 patch | Source0 only |

When sources drift between the spec directory and `~/rpmbuild/SOURCES/`, the build silently uses the stale copies. Re-copying before `rpmbuild -bs` is cheap insurance.

## Linting

All specs are kept at **zero rpmlint warnings**. Run from the repo root with the
bundled config:

```bash
sudo dnf install rpmlint        # once
rpmlint -c rpmlint.toml */*.spec
# expect: 0 errors, 0 warnings, 0 badness
```

`-c rpmlint.toml` adds two repo-local filters on top of Fedora's defaults:

- `no-%check-section` — suppressed for the 6 specs with no test to run (the 4
  icon themes, the kvmfr akmod, the GJS extension). The 5 vinceliuice GTK themes,
  llama.cpp, and looking-glass-client carry a real `%check`.
- `spelling-error '(json|ekthor)'` — `json` (part of `config.json`) and `ekthor`
  (the extension's UUID author tag) are correct, not misspellings.

The GTK-theme `%check` parses the compiled `gtk-4.0` CSS through the real GTK 4
engine (`GtkCssProvider`) and asserts the GNOME 50 selectors compiled into
`gnome-shell.css`. Every other warning class is fixed in the specs
(`%setup -q`/`%autosetup`, an explicit `%build`, `%%`-escaped `%changelog`
macros), so a plain `rpmlint */*.spec` only surfaces the filtered
`no-%check-section` (6 specs).

## COPR

The `raro28/wdm` COPR builds these from SRPMs uploaded via `copr-cli`, or via the Custom method pulling from this repo. COPR's chroot matches `mock -r fedora-44-x86_64` exactly — anything that builds locally builds there.

## Repo layout

```
.
├── README.md                              # this file
├── rpmlint.toml                           # repo-local rpmlint filter (see Linting)
├── <spec-dir>/
│   ├── <spec-name>.spec
│   ├── README.md                          # only where extra runtime/cutover docs apply
│   └── [local source files referenced as SourceN]
└── ...
```

Each subdirectory is self-contained: the spec plus the local source files it references.
