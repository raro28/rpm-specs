Name:           tela-circle-icon-theme
Version:        20260707
Release:        1%{?dist}
Summary:        A flat colorful Design icon theme

BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Tela-circle-icon-theme
%define dversion 2026-07-07
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz#/%{dname}-%{dversion}.tar.gz

BuildRequires:  gtk-update-icon-cache

%description
A flat colorful Design icon theme

%prep
%setup -q -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
./install.sh -d "%{buildroot}%{_datarootdir}/icons" -c standard

%files
%{_datarootdir}/icons

%changelog
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
