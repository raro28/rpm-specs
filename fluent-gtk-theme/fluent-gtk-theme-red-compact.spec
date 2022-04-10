Name:           fluent-gtk-theme-red-compact
Version:        20220115
Release:        2%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch: noarch

License:        GPLv3+

%define dname Fluent-gtk-theme
%define dversion 2022-01-15
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
./install.sh --dest %{buildroot}%{_datarootdir}/themes --theme red -i fedora --size compact --tweaks solid round

%files
%{_datarootdir}/themes

%changelog
* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220115-2
- add gnome-shell

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220115-1
- Initial version of the package