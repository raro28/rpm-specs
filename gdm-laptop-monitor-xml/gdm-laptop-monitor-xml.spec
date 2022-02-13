Name:           gdm-laptop-monitor-xml
Version:        0.0.0
Release:        1%{?dist}
Summary:        GDM laptop monitor xml

License:        GPLv3+
URL:            https://github.com/raro28/gdm-laptop-monitor-xml
Source0:        https://github.com/raro28/gdm-laptop-monitor-xml/releases/download/%{version}/gdm-laptop-monitor-xml-%{version}.tar.gz

Requires:       gdm

%description
GDM laptop monitor xml

%prep
%autosetup

%install
mkdir -p %{buildroot}%{_sysconfdir}/skel/.config
cp -a ./etc/skel/.config/monitors.xml %{buildroot}%{_sysconfdir}/skel/.config

%files
%attr(0644,root,root) %{_sysconfdir}/skel/.config/monitors.xml

%changelog
* Sun Feb 13 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-1
- Initial version of the package