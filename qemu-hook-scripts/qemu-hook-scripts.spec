Name:           qemu-hook-scripts
Version:        0.0.0
Release:        3%{?dist}
Summary:        QEMU hook scripts

License:        GPLv3+
URL:            https://github.com/raro28/qemu-hook-scripts
Source0:        https://github.com/raro28/qemu-hook-scripts/releases/download/%{version}/qemu-hook-scripts-%{version}.tar.gz

Requires:       bash
Requires:       systemd
Requires:       libvirt-daemon

%description
QEMU hook scripts

%prep
%autosetup

%install
mkdir -p %{buildroot}%{_sysconfdir}/libvirt/hooks
cp -a ./etc/libvirt/hooks/qemu %{buildroot}%{_sysconfdir}/libvirt/hooks/.

%files
%attr(0755,root,root) %{_sysconfdir}/libvirt/hooks/qemu

%post
systemctl is-active libvirtd && systemctl restart libvirtd || $(exit 0)

%postun
systemctl is-active libvirtd && systemctl restart libvirtd || $(exit 0)

%changelog
* Sat Feb 12 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-3
- Override exit code

* Sat Feb 12 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-2
- Fix systemctl unit reference
- Add dependencies

* Sat Feb 12 2022 Hector Diaz <hdiazc@live.com> - 0.0.0-1
- Initial version of the package