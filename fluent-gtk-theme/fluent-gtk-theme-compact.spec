Name:           fluent-gtk-theme-compact
Version:        20240612
Release:        2%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch: noarch

License:        GPLv3+

%define dname Fluent-gtk-theme
%define dversion 2024-06-12
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
./install.sh --dest %{buildroot}%{_datarootdir}/themes --theme grey -i gnome --size compact --tweaks solid round -c dark

%files
%{_datarootdir}/themes

%changelog
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