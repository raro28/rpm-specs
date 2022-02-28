Name:           tela-circle-icon-black-theme
Version:        20220208
Release:        1%{?dist}
Summary:        A flat colorful Design icon theme

BuildArch:      noarch

License:        GPLv3+

%define dname Tela-circle-icon-theme
%define dversion 2022-02-08
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires:  gtk-update-icon-cache

%description
A flat colorful Design icon theme

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
./install.sh -d "%{buildroot}%{_datarootdir}/icons" -c black

%files
%{_datarootdir}/icons

%changelog
* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220208-1
- Initial version of the package