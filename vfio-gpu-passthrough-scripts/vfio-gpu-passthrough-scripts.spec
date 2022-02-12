Name:           vfio-gpu-passthrough-scripts
Version:        0.0.1
Release:        1%{?dist}
Summary:        Helper scripts for gpu passthrough

License:        GPLv3+
URL:            https://github.com/raro28/vfio-gpu-passthrough-scripts
Source0:        https://github.com/raro28/vfio-gpu-passthrough-scripts/releases/download/0.0.0/vfio-gpu-passthrough-scripts-%{version}.tar.gz   

%description
Helper scripts for gpu passthrough


%prep
%autosetup

%install

mkdir -p %{buildroot}%{_prefix}/lib/dracut/modules.d/20vfio/
cp -a ./usr/lib/dracut/modules.d/20vfio/* %{buildroot}%{_prefix}/lib/dracut/modules.d/20vfio/.

mkdir -p %{buildroot}%{_bindir}
cp -a ./usr/bin/checkiommu %{buildroot}%{_bindir}/.

mkdir -p %{buildroot}%{_sysconfdir}/dracut.conf.d
cp -a ./etc/dracut.conf.d/vfio.conf %{buildroot}%{_sysconfdir}/dracut.conf.d/.

%files
%attr(0755,root,root) %{_prefix}/lib/dracut/modules.d/20vfio/module-setup.sh
%attr(0755,root,root) %{_prefix}/lib/dracut/modules.d/20vfio/vfio-pci-override.sh
%attr(0755,root,root) %{_bindir}/checkiommu
%attr(0644,root,root) %{_sysconfdir}/dracut.conf.d/vfio.conf



%changelog
* Sat Feb 12 2022 Hector Diaz <hdiazc@live.com>
- Initial version of the package
