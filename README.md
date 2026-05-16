# rpm-specs

RPM spec files for Fedora 44 packages I maintain in the COPR
[raro28/wdm](https://copr.fedorainfracloud.org/coprs/raro28/wdm/).
Each subdirectory is one source package.

## Specs in this repo

| Spec | Current build | What it ships |
|---|---|---|
| colloid-gtk-theme | `20250731-4` | GTK theme (vinceliuice) |
| fluent-gtk-theme-compact | `20250417-5` | GTK theme (vinceliuice) |
| looking-glass-client | `7.0.0-13` | Looking Glass B7 client + SELinux subpackage |
| looking-glass-kvmfr-kmod | `0.0.12-7` | akmod for the `kvmfr` kernel module — see [its README](looking-glass-kvmfr-kmod/README.md) |
| orchis-theme | `20250425-4` | GTK theme (vinceliuice) |
| qogir-icon-theme | `20250215-3` | Icon theme (vinceliuice) |
| qogir-theme | `20250817-4` | GTK theme (vinceliuice) |
| tela-circle-icon-theme | `20250210-3` | Icon theme (vinceliuice) |
| tela-icon-theme | `20250210-1` | Icon theme (vinceliuice) |
| whitesur-gtk-theme | `20250724-4` | GTK theme (vinceliuice) |
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

The nine theme specs from vinceliuice have only `Source0` (a GitHub tarball). The workflow is the canonical 4 steps; nothing to copy.

Example with `qogir-theme`:

```bash
spectool -g -R qogir-theme/qogir-theme.spec
rpmbuild -bs qogir-theme/qogir-theme.spec
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/qogir-theme-20250817-4.fc44.src.rpm
```

Substitute the spec path / SRPM filename for any of:

- `colloid-gtk-theme`
- `fluent-gtk-theme-compact`
- `orchis-theme`
- `qogir-icon-theme`
- `qogir-theme`
- `tela-circle-icon-theme`
- `tela-icon-theme`
- `whitesur-gtk-theme`
- `whitesur-icon-theme`

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
mock -r fedora-44-x86_64 ~/rpmbuild/SRPMS/looking-glass-client-7.0.0-13.fc44.src.rpm
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
| All 9 theme/icon specs | No | Source0 only |
| looking-glass-client | **Yes** — 4 files | Source0 + 6 submodule URLs |
| looking-glass-kvmfr-kmod | **Yes** — 5 files + 1 patch | Source0 only |

When sources drift between the spec directory and `~/rpmbuild/SOURCES/`, the build silently uses the stale copies. Re-copying before `rpmbuild -bs` is cheap insurance.

## COPR

The `raro28/wdm` COPR builds these from SRPMs uploaded via `copr-cli`, or via the Custom method pulling from this repo. COPR's chroot matches `mock -r fedora-44-x86_64` exactly — anything that builds locally builds there.

## Repo layout

```
.
├── README.md                              # this file
├── <spec-dir>/
│   ├── <spec-name>.spec
│   ├── README.md                          # only where extra runtime/cutover docs apply
│   └── [local source files referenced as SourceN]
└── ...
```

Each subdirectory is self-contained: the spec plus the local source files it references.
