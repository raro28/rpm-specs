Name:           orchis-theme
Version:        20241103
Release:        1%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPLv3+

%define dname Orchis-theme
%define dversion 2024-11-03
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

Requires:       gtk-murrine-engine

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
* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241103-1
- Initial version of the package