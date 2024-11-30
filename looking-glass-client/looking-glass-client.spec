Name:           looking-glass-client
Version:        B7.0.0
Release:        1%{?dist}
Summary:        Low latency KVMFR implementation for guests with VGA PCI Passthrough

License:        GPLv2
Source0:        https://github.com/raro28/%{name}/releases/download/%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}.desktop
Source2:        10-%{name}.conf
#Source3:        %{name}-tmp.cil

Requires:       systemd
Requires:       dejavu-sans-mono-fonts
Requires:       texlive-gnu-freefont
Requires:       policycoreutils

BuildRequires:       desktop-file-utils
BuildRequires:       coreutils
BuildRequires:       binutils-devel
BuildRequires:       cmake
BuildRequires:       fontconfig-devel
BuildRequires:       gcc
BuildRequires:       gcc-c++
BuildRequires:       libglvnd-devel
BuildRequires:       libX11-devel
BuildRequires:       libXcursor-devel
BuildRequires:       libXfixes-devel
BuildRequires:       libXi-devel
BuildRequires:       libXinerama-devel
BuildRequires:       libxkbcommon-x11-devel
BuildRequires:       libXpresent-devel
BuildRequires:       libXrandr-devel
BuildRequires:       libXScrnSaver-devel
BuildRequires:       make
BuildRequires:       nettle-devel
BuildRequires:       pkgconf-pkg-config
BuildRequires:       SDL2-devel
BuildRequires:       SDL2_ttf-devel
BuildRequires:       spice-protocol
BuildRequires:       wayland-devel
BuildRequires:       wayland-protocols-devel
BuildRequires:       libsamplerate-devel
BuildRequires:       pipewire-devel
BuildRequires:       pulseaudio-libs-devel

%description
Looking Glass is an open source application that allows the use of a KVM 
(Kernel-based Virtual Machine) configured for VGA PCI Pass-through 
without an attached physical monitor, keyboard or mouse. This is the final 
step required to move away from dual booting with other operating systems 
for legacy programs that require high performance graphics.

%prep
%autosetup

%build
mkdir ./client/build
pushd client/build
%cmake ../
pushd redhat-linux-build
make -j`nproc`
popd
popd

%install
mkdir -p %{buildroot}%{_bindir}
cp -a ./client/build/redhat-linux-build/%{name} %{buildroot}%{_bindir}/.

mkdir -p %{buildroot}%{_datadir}/pixmaps
cp -a ./resources/lg-logo.png %{buildroot}%{_datadir}/pixmaps/%{name}.png

mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/tmpfiles.d/.

desktop-file-install                                    \
--delete-original                                       \
--dir=%{buildroot}%{_datadir}/applications              \
%{SOURCE1}

%files
%attr(0755,root,root) %{_bindir}/%{name}
%attr(0644,root,root) %{_datadir}/pixmaps/%{name}.png
%attr(0644,root,root) %{_datadir}/applications/%{name}.desktop
%attr(0644,root,root) %{_sysconfdir}/tmpfiles.d/10-%{name}.conf

%post
systemd-tmpfiles --create %{_sysconfdir}/tmpfiles.d/10-%{name}.conf
#semodule -i %{name}-tmp.cil

%postun
systemd-tmpfiles --remove %{_sysconfdir}/tmpfiles.d/10-%{name}.conf
#semodule -r %{name}-tmp.cil

%changelog
* Sat Jun 29 2024 Hector Diaz <hdiazc@live.com> - B7.0.0-2
- Update to B7-rc1

* Fri Jan 6 2023 Hector Diaz <hdiazc@live.com> - B6.0.0-1
- B6 release

* Sat Feb 26 2022 Hector Diaz <hdiazc@live.com> - B5.0.1-2
- Remote packaged tar.gz

* Sun Feb 13 2022 Hector Diaz <hdiazc@live.com> - B5.0.1-1
- Initial version of the package
