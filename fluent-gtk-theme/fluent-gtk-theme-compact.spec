Name:           fluent-gtk-theme-compact
Version:        20250417
Release:        3%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Fluent-gtk-theme
%define dversion 2025-04-17
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

Requires:       gnome-themes-extra
Requires:       gtk-murrine-engine

BuildRequires:  gnome-shell
BuildRequires:  sassc

%description
Fluent is a Fluent design theme for GNOME/GTK based desktop environments

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh --dest %{buildroot}%{_datarootdir}/themes --theme grey -i gnome --size compact --tweaks solid round -l

%files
%{_datarootdir}/themes

%changelog
* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250417-3
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add -l (libadwaita) to install.sh for GTK4/libadwaita app theming

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250417-2
- Include light

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250417-1
- Bump version

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20240612-2
- Dark theme only

* Sat Nov 30 2024 Hector Diaz <hdiazc@live.com> - 20240612-1
- Bump version

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20221215-1
- Bump version

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220115-2
- add gnome-shell

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220115-1
- Initial version of the package