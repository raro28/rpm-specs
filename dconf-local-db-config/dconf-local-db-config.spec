Name:           dconf-local-db-config
Version:        0.0.2
Release:        2%{?dist}
Summary:        Dconf local db config files

License:        GPLv3+
URL:            https://github.com/raro28/%{name}
Source0:        https://github.com/raro28/%{name}/archive/refs/tags/%{version}.tar.gz

Requires:       dconf

%description
Dconf local db config files

%prep
%autosetup

%install
mkdir -p %{buildroot}%{_sysconfdir}/dconf/db/local.d
cp -a ./etc/dconf/db/local.d/00-appearance %{buildroot}%{_sysconfdir}/dconf/db/local.d/.
cp -a ./etc/dconf/db/local.d/01-behaviour %{buildroot}%{_sysconfdir}/dconf/db/local.d/.
cp -a ./etc/dconf/db/local.d/02-shell %{buildroot}%{_sysconfdir}/dconf/db/local.d/.

%files
%attr(0644,root,root) %{_sysconfdir}/dconf/db/local.d/00-appearance
%attr(0644,root,root) %{_sysconfdir}/dconf/db/local.d/01-behaviour
%attr(0644,root,root) %{_sysconfdir}/dconf/db/local.d/02-shell

%post
dconf update

%postun
dconf update

%changelog
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