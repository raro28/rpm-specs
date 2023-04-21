Name:           tela-circle-icon-black-theme
Version:        20230416
Release:        1%{?dist}
Summary:        A flat colorful Design icon theme

BuildArch:      noarch

License:        GPLv3+

%define dname Tela-circle-icon-theme
%define dversion 2023-04-16
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
* Fri Apr 21 2023 Hector Diaz <hdiazc@live.com> - 20230416-1
- Bump version

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230129-1
- Bump version

* Sun Mar 12 2022 Hector Diaz <hdiazc@live.com> - 20220307-1
- Update sources

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220208-1
- Initial version of the package