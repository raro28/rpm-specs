Name:           qogir-theme
Version:        20250817
Release:        4%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Qogir-theme
%define dversion 2025-08-17
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires:  gnome-shell
BuildRequires:  sassc

%description
Qogir is a flat Design theme for GTK 3, GTK 2 
and Gnome-Shell which supports GTK 3 and GTK 2 
based desktop environments like Gnome, Unity, Budgie, 
Cinnamon Pantheon, XFCE, Mate, etc

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh --icon gnome --tweaks round --libadwaita --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250817-4
- Drop GTK2-era runtime deps (adwaita-gtk2-theme, gtk-murrine-engine,
  gtk2-engines): adwaita-gtk2-theme was removed from Fedora 44 repos,
  and the gtk-2.0/ payload only matters for legacy GTK2 apps

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250817-3
- Replace gnome-themes-extra dep with Fedora's adwaita-gtk2-theme

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250817-2
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add gnome-themes-extra runtime dependency

* Sat Dec 13 2025 Hector Diaz <hdiazc@live.com> - 20250817-1
- Bump version

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20240522-3
- Include light

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20240522-2
- Dark theme only

* Sat Nov 30 2024 Hector Diaz <hdiazc@live.com> - 20240522-1
- Bump version

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230227-2
- Set options

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230227-1
- Bump version

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20211225-2
- add gnome-shell

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20211225-1
- Initial version of the package