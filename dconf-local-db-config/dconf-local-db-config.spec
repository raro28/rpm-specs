Name:           dconf-local-db-config
Version:        0.0.0
Release:        1%{?dist}
Summary:        Dconf local db config files

License:        GPLv3+
URL:            https://github.com/raro28/dconf-local-db-config
Source0:        https://github.com/raro28/dconf-local-db-config/releases/download/%{version}/dconf-local-db-config-%{version}.tar.gz

Requires:       gdm

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
* Sun Feb 13 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-1
- Initial version of the package