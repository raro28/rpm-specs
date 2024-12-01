Name:           qogir-icon-theme
Version:        20230605
Release:        1%{?dist}
Summary:        A flat colorful design icon theme for linux desktops
BuildArch:      noarch

License:        GPLv3+

%define dname Qogir-icon-theme
%define dversion 2023-06-05
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dname}-%{dversion}.tar.gz

BuildRequires:  gtk-update-icon-cache

%description
A flat colorful design icon theme for linux desktops

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
./install.sh --theme default -c dark --dest "%{buildroot}%{_datarootdir}/icons"

%files
%{_datarootdir}/icons

%changelog
* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20230605-1
- Bump versions

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-4
- Remove only dark variant

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-3
- Fix typo

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-2
- Set options

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-1
- Bump version

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220112-1
- Initial version of the package