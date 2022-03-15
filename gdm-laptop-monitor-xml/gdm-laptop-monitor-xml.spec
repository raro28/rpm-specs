Name:           gdm-laptop-monitor-xml
Version:        0.0.0
Release:        4%{?dist}
Summary:        GDM laptop monitor xml

License:        GPLv3+
URL:            https://github.com/raro28/%{name}
Source0:        monitors.xml

Requires:       gdm

%description
GDM laptop monitor xml

%prep

%install
mkdir -p %{buildroot}%{_sysconfdir}/skel/.config
cp -a %{SOURCE0} %{buildroot}%{_sysconfdir}/skel/.config

mkdir -p %{buildroot}%{_sharedstatedir}/gdm/.config
cp -a %{SOURCE0} %{buildroot}%{_sharedstatedir}/gdm/.config

%files
%attr(0644,root,root) %{_sysconfdir}/skel/.config/monitors.xml
%attr(0644,gdm,gdm) %{_sharedstatedir}/gdm/.config/monitors.xml

%changelog
* Tue Mar 15 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-4
- Track source

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-3
- Change source url

* Thu Feb 17 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-2
- Configure GDM

* Sun Feb 13 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-1
- Initial version of the package