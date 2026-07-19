Name:           qogir-icon-theme
Version:        20250215
Release:        5%{?dist}
Summary:        A flat colorful design icon theme for linux desktops
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Qogir-icon-theme
%define dversion 2025-02-15
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires:  gtk-update-icon-cache

%description
A flat colorful design icon theme for linux desktops

%prep
%setup -q -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
# -t selects distro branding, not accent color, so only the default ships.
./install.sh --theme default --color all --dest "%{buildroot}%{_datarootdir}/icons"
# install.sh copies COPYING into every theme dir; %%license COPYING already
# ships it once, so drop the per-theme copies (files-duplicated-waste).
find %{buildroot}%{_datarootdir}/icons -name COPYING -delete

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

%files
%license COPYING
%{_datarootdir}/icons/Qogir
%{_datarootdir}/icons/Qogir-Light
%{_datarootdir}/icons/Qogir-Dark

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250215-5
- No color split: Qogir's -t selects distro branding (default|manjaro|ubuntu),
  not accent color, so only the default variant ships.
- Add a %%check: index.theme gate and a zero-dangling-symlink gate.
- Drop per-theme COPYING copies install.sh creates in Qogir/Qogir-Light/
  Qogir-Dark: %%license COPYING already ships it once (files-duplicated-waste).

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250215-4
- Own only the installed theme directories, not %%{_datarootdir}/icons itself:
  that directory belongs to the filesystem package, and co-owning it is the
  standard-dir-owned-by-package defect.

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250215-3
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250215-2
- Include light

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250215-1
- Bump version

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20230605-1
- Bump versions

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-4
- Remove only dark variant

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-3
- Fix typo

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-2
- Set options

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-1
- Bump version

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220112-1
- Initial version of the package
