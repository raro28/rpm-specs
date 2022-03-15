Name:           dconf-local-db-config
Version:        0.0.5
Release:        3%{?dist}
Summary:        Dconf local db config files

License:        GPLv3+
URL:            https://github.com/raro28/%{name}
Source0:        00-appearance
Source1:        01-behaviour
Source2:        02-shell
Source3:        03-virt

Requires:       dconf

%description
Dconf local db config files

%prep

%install
mkdir -p %{buildroot}%{_sysconfdir}/dconf/db/local.d
cp -a %{SOURCE0} %{buildroot}%{_sysconfdir}/dconf/db/local.d/.
cp -a %{SOURCE1} %{buildroot}%{_sysconfdir}/dconf/db/local.d/.
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/dconf/db/local.d/.
cp -a %{SOURCE3} %{buildroot}%{_sysconfdir}/dconf/db/local.d/.

%files
%{_sysconfdir}/dconf/db/local.d

%post
dconf update

%postun
dconf update

%changelog
* Tue Mar 15 2022 Hector Diaz <hdiazc@live.com> - 0.0.5-3
- Track sources

* Sat Mar 12 2022 Hector Diaz <hdiazc@live.com> - 0.0.5-1
- Update sources

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 0.0.4-1
- Update sources

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 0.0.3-1
- Update sources

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 0.0.2-2
- Remove gdm

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 0.0.2-1
- Update sources

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 0.0.1-2
- Update dependencies

* Mon Feb 14 2022 Hector Diaz <hdiazc@live.com> - 0.0.1-1
- Initial version of the package

* Sun Feb 13 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-1
- Initial version of the package