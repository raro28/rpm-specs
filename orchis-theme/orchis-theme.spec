Name:           orchis-theme
Version:        20250425
Release:        4%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Orchis-theme
%define dversion 2025-04-25
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires:  gnome-shell
BuildRequires:  sassc

%description
Orchis is a Material Design theme for GNOME/GTK based desktop environments.
Based on nana-4 -- materia-theme

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh --icon gnome -t grey -c dark --libadwaita --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250425-4
- Drop GTK2-era runtime deps (adwaita-gtk2-theme, gtk-murrine-engine):
  adwaita-gtk2-theme was removed from Fedora 44 repos, and the gtk-2.0/
  payload only matters for legacy GTK2 apps

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250425-3
- Replace gnome-themes-extra dep with Fedora's adwaita-gtk2-theme

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250425-2
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add gnome-themes-extra runtime dependency

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250425-1
- Bump version

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241103-1
- Initial version of the package