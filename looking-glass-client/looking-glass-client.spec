Name:           looking-glass-client
Version:        B5.0.1
Release:        1%{?dist}
Summary:        Low latency KVMFR implementation for guests with VGA PCI Passthrough

License:        GPLv2
Source0:        looking-glass-client-%{version}.tar.gz   

Requires:       dejavu-sans-mono-fonts
Requires:       texlive-gnu-freefont

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
cp -a ./client/build/redhat-linux-build/looking-glass-client %{buildroot}%{_bindir}/.

%files
%attr(0755,root,root) %{_bindir}/looking-glass-client

%changelog
* Sun Feb 13 2022 Hector Diaz <hdiazc@live.com> - B5.0.1-1
- Initial version of the package