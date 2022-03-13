Name:           user-files
Version:        0.0.1
Release:        1%{?dist}
Summary:        User files

License:        GPLv3+
URL:            https://github.com/raro28/%{name}
Source0:        https://github.com/raro28/%{name}/archive/refs/tags/%{version}.tar.gz

%description
User files

%prep
%autosetup

%install
mkdir -p %{buildroot}%{_sysconfdir}/skel/
cp -a ./etc/skel/.config %{buildroot}%{_sysconfdir}/skel/.

%files
%{_sysconfdir}/skel/.config

%changelog
* Sun Mar 13 2022 Hector Diaz <hdiazc@live.com> - 0.0.1-1
- Bump version

* Sun Mar 13 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-1
- Initial version of the package