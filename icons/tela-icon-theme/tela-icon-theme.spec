Name:           tela-icon-theme
Version:        20260707
Release:        4%{?dist}
Summary:        A flat colorful Design icon theme
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Tela-icon-theme
%define dversion 2026-07-07
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz#/%{dname}-%{dversion}.tar.gz
Patch0:         fix-dangling-symlinks.patch

BuildRequires:  gtk-update-icon-cache

%description
A flat colorful Design icon theme.

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

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
# Tela takes colors as positional arguments; it has no -t flag.
./install.sh -d "%{buildroot}%{_datarootdir}/icons" blue red grey

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

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-4
- Split into color packages (blue, red, grey). Tela takes colors as positional
  arguments, not flags.

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-3
- Own only the installed theme directories, not %%{_datarootdir}/icons itself:
  that directory belongs to the filesystem package, and co-owning it is the
  standard-dir-owned-by-package defect.

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-2
- Patch0 (fix-dangling-symlinks): links/symbolic/apps/xsi-addon-symbolic.svg
  targets application-x-addon-symbolic.svg as a sibling, but that icon lives in
  symbolic/mimetypes, so the alias shipped broken. Repoint it via install.sh.
  Verified: dangling symlinks 6 -> 0 across a 9-theme build.
- Switch %%prep to %%autosetup -p1 to apply the patch.
- Add a %%check: assert every theme has an index.theme and that no dangling
  symlink survives.

* Sat Jul 11 2026 Hector Diaz <hdiazc@live.com> - 20260707-1
- Bump to upstream 2026-07-07 (install.sh flags unchanged: -d <dest> standard)

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250210-1
- Initial version of the package
