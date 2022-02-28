Name:           qogir-theme
Version:        20211225
Release:        1%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPLv3+

%define dname Qogir-theme
%define dversion 2021-12-25
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

Requires:       gtk2-engines
Requires:       gtk-murrine-engine

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
./install.sh --dest %{buildroot}%{_datarootdir}/themes --theme default -l fedora --tweaks round

%files
%{_datarootdir}/themes

%changelog
* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20211225-1
- Initial version of the package