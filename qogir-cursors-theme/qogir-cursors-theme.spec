Name:           qogir-cursors-theme
Version:        20230223
Release:        1%{?dist}
Summary:        A flat colorful design icon theme for linux desktops
BuildArch:      noarch

License:        GPLv3+

%define dname Qogir-icon-theme
%define dversion 2023-02-23
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

%description
A flat colorful design icon theme for linux desktops

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
cp -r ./src/cursors/dist/ %{buildroot}%{_datarootdir}/icons/Qogir-cursors
cp -r ./src/cursors/dist-dark/ %{buildroot}%{_datarootdir}/icons/Qogir-white-cursors

%files
%{_datarootdir}/icons

%changelog
* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230223-1
- Bump version

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220112-1
- Initial version of the package