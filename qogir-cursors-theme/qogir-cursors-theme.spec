Name:           qogir-cursors-theme
Version:        20230605
Release:        2%{?dist}
Summary:        A flat colorful design icon theme for linux desktops
BuildArch:      noarch

License:        GPLv3+

%define dname Qogir-icon-theme
%define dversion 2023-06-05
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dname}-%{dversion}.tar.gz

%description
A flat colorful design icon theme for linux desktops

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
cp -r ./src/cursors/dist-dark/ %{buildroot}%{_datarootdir}/icons/Qogir-white-cursors

%files
%{_datarootdir}/icons

%changelog
* Sat Nov 30 2024 Hector Diaz <hdiazc@live.com> - 20230605-2
- Only white cursors

* Sat Nov 30 2024 Hector Diaz <hdiazc@live.com> - 20230605-1
- Bump version

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-1
- Bump version

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220112-1
- Initial version of the package