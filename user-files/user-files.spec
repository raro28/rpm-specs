Name:           user-files
Version:        0.0.1
Release:        2%{?dist}
Summary:        User files

License:        GPLv3+
URL:            https://github.com/raro28/%{name}
Source0:        mimeapps.list

%description
User files

%prep

%install
mkdir -p %{buildroot}%{_sysconfdir}/skel/.config
cp -a %{SOURCE0} %{buildroot}%{_sysconfdir}/skel/.config/.

%files
%{_sysconfdir}/skel/.config

%changelog
* Tue Mar 15 2022 Hector Diaz <hdiazc@live.com> - 0.0.1-2
- Bump version

* Sun Mar 13 2022 Hector Diaz <hdiazc@live.com> - 0.0.1-1
- Bump version

* Sun Mar 13 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-1
- Initial version of the package