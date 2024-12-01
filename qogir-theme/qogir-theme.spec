Name:           qogir-theme
Version:        20240522
Release:        2%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPLv3+

%define dname Qogir-theme
%define dversion 2024-05-22
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dname}-%{dversion}.tar.gz

Requires:       gtk2-engines
Requires:       gtk-murrine-engine

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
./install.sh --icon fedora -c dark --tweaks round --libadwaita --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
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