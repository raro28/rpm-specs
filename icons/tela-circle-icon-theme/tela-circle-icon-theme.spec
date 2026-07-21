Name:           tela-circle-icon-theme
Version:        20260707
Release:        4%{?dist}
Summary:        A flat colorful Design icon theme

BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Tela-circle-icon-theme
%define dversion 2026-07-07
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz#/%{dname}-%{dversion}.tar.gz
Patch0:         fix-dangling-symlinks.patch

BuildRequires:  gtk-update-icon-cache

%description
A flat colorful Design icon theme

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

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
# -c enables the circular folder version and takes no argument; the colors
# that follow are positional.
./install.sh -d "%{buildroot}%{_datarootdir}/icons" -c blue red grey

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

# Tela-circle upstream ships no license file and its README makes no license
# statement, so there is no %%license to install. The License: tag is inherited
# from the sibling Tela-icon-theme; verifying it with upstream is a separate task.
%files
%files blue
%{_datarootdir}/icons/Tela-circle-blue
%{_datarootdir}/icons/Tela-circle-blue-light
%{_datarootdir}/icons/Tela-circle-blue-dark

%files red
%{_datarootdir}/icons/Tela-circle-red
%{_datarootdir}/icons/Tela-circle-red-light
%{_datarootdir}/icons/Tela-circle-red-dark

%files grey
%{_datarootdir}/icons/Tela-circle-grey
%{_datarootdir}/icons/Tela-circle-grey-light
%{_datarootdir}/icons/Tela-circle-grey-dark

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-4
- Split into color packages (blue, red, grey). Note -c enables the circular
  folder version and takes no argument; colors are positional, so the previous
  "-c standard" meant "circular, color standard".

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-3
- Own only the installed theme directories, not %%{_datarootdir}/icons itself:
  that directory belongs to the filesystem package, and co-owning it is the
  standard-dir-owned-by-package defect.

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-2
- Patch0 (fix-dangling-symlinks): repair three upstream alias defects --
  xsi-addon-symbolic.svg targeting the wrong directory; CherryStudio.svg whose
  symlink target carries a literal trailing newline ("cherrystudio.svg\n") so it
  never resolves; and org.xfce.appfinder.svg pointing at edit-find.svg, which
  exists only under 16/22/24/actions, so the dead alias is dropped.
  Verified: dangling symlinks 12 -> 0 across a 9-theme build.
- Switch %%prep to %%autosetup -p1 to apply the patch.
- Add a %%check: index.theme gate plus a zero-dangling-symlink gate.

* Sat Jul 11 2026 Hector Diaz <hdiazc@live.com> - 20260707-1
- Bump to upstream 2026-07-07 (install.sh flags unchanged: -d <dest> -c standard)

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250210-3
- Rename package: drop 'black' from name, switch to standard color variant
  (install.sh -c standard instead of -c black)

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250210-2
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250210-1
- Bump version

* Sat Nov 30 2024 Hector Diaz <hdiazc@live.com> - 20241115-1
- Bump version

* Fri Apr 21 2023 Hector Diaz <hdiazc@live.com> - 20230416-1
- Bump version

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230129-1
- Bump version

* Sat Mar 12 2022 Hector Diaz <hdiazc@live.com> - 20220307-1
- Update sources

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220208-1
- Initial version of the package
