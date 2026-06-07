Name:           colloid-gtk-theme
Version:        20250731
Release:        4%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Colloid-gtk-theme
%define dversion 2025-07-31
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires:  gnome-shell
BuildRequires:  sassc

%description
Theme for GNOME/GTK based desktop environments.

%prep
%setup -q -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh -t grey --libadwaita --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250731-4
- Drop GTK2-era runtime deps (adwaita-gtk2-theme, gtk-murrine-engine):
  adwaita-gtk2-theme was removed from Fedora 44 repos, and the gtk-2.0/
  payload only matters for legacy GTK2 apps

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250731-3
- Replace gnome-themes-extra dep with Fedora's adwaita-gtk2-theme

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250731-2
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add gnome-themes-extra runtime dependency

* Sat Dec 13 2025 Hector Diaz <hdiazc@live.com> - 20250731-1
- Bump version

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20241116-2
- Include light

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241116-1
- Initial version of the package
