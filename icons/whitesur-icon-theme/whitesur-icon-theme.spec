Name:           whitesur-icon-theme
Version:        20260707
Release:        3%{?dist}
Summary:        A macOS BigSur-like icon theme for Linux desktops
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname WhiteSur-icon-theme
%define dversion 2026-07-07
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz
Patch0:         fix-dangling-symlinks.patch

BuildRequires:  gtk-update-icon-cache

%description
A macOS BigSur-like icon theme for Linux desktops.

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
./install.sh --theme default --alternative --dest "%{buildroot}%{_datarootdir}/icons"

%check
# Every installed theme must carry an index.theme.
n=0
for d in %{buildroot}%{_datadir}/icons/*/; do
  n=$((n+1))
  [ -f "$d/index.theme" ] || { echo "FAIL: no index.theme in $d"; exit 1; }
done
[ "$n" -gt 0 ] || { echo "FAIL: no icon themes installed"; exit 1; }
echo "index.theme gate: OK ($n themes)"
# Patch0 repairs every broken alias upstream ships; assert none come back.
dangling=$(find %{buildroot}%{_datadir}/icons -xtype l | wc -l)
[ "$dangling" -eq 0 ] || {
  echo "FAIL: $dangling dangling symlink(s):"
  find %{buildroot}%{_datadir}/icons -xtype l -printf '  %p -> %l\n' | head -20
  exit 1
}
echo "dangling-symlink gate: OK (0 across $n themes)"

%files
%{_datarootdir}/icons/*

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-3
- Own only the installed theme directories, not %%{_datarootdir}/icons itself:
  that directory belongs to the filesystem package, and co-owning it is the
  standard-dir-owned-by-package defect.

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-2
- Patch0 (fix-dangling-symlinks): two upstream defects. (1) install.sh copied
  links/ over the already-installed icons with plain cp -r, so any alias sharing
  a name with a real icon replaced it with a symlink to itself -- affinity,
  bold-brew, gittyup, helium, HTTrack, HTTrack-download, lm_studio, VirusTotal
  and the tubefeeder pair all shipped as broken self-links, i.e. those apps had
  no icon at all. Use cp -rn so an alias never clobbers the icon it names.
  (2) src/status/22 ships no weather-clear-night.svg although links/status/22
  holds 36 aliases pointing at it; supply it from the 32px source.
  Verified: dangling symlinks 249 -> 0 across a 9-theme build, and the ten
  clobbered icons are restored as real files.
- Switch %%prep to %%autosetup -p1 to apply the patch.
- Add a %%check: index.theme gate plus a zero-dangling-symlink gate.

* Sat Jul 11 2026 Hector Diaz <hdiazc@live.com> - 20260707-1
- Bump to upstream 2026-07-07 (install.sh flags unchanged:
  --theme default --alternative --dest)

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20251227-1
- Initial version of the package
