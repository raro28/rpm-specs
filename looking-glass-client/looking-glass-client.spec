%global upstream_version B7.0.0
%global selinux_modulename %{name}

Name:           looking-glass-client
Version:        7.0.0
Release:        9%{?dist}
Summary:        Low latency KVMFR implementation for guests with VGA PCI Passthrough

License:        GPL-2.0-only
URL:            https://looking-glass.io/
Source0:        https://github.com/raro28/%{name}/releases/download/%{upstream_version}/%{name}-%{upstream_version}.tar.gz
Source1:        %{name}.desktop
Source2:        10-%{name}.conf
Source3:        %{name}.te
Source4:        %{name}.fc

Requires:       font(dejavusansmono)
Requires:       texlive-gnu-freefont
Recommends:     %{name}-selinux = %{version}-%{release}

BuildRequires:       desktop-file-utils
BuildRequires:       coreutils
BuildRequires:       cmake
BuildRequires:       fontconfig-devel
BuildRequires:       gcc
BuildRequires:       gcc-c++
BuildRequires:       libglvnd-devel
BuildRequires:       libxkbcommon-devel
BuildRequires:       libdecor-devel
BuildRequires:       nettle-devel
BuildRequires:       pkgconf-pkg-config
BuildRequires:       spice-protocol
BuildRequires:       wayland-devel
BuildRequires:       wayland-protocols-devel
BuildRequires:       libsamplerate-devel
BuildRequires:       pipewire-devel
BuildRequires:       selinux-policy-devel

%description
Looking Glass is an open source application that allows the use of a KVM
(Kernel-based Virtual Machine) configured for VGA PCI Pass-through
without an attached physical monitor, keyboard or mouse. This is the final
step required to move away from dual booting with other operating systems
for legacy programs that require high performance graphics.

%package selinux
Summary:        SELinux policy module for %{name}
BuildArch:      noarch
%{?selinux_requires}
Requires(post): %{name} = %{version}-%{release}

%description selinux
SELinux policy module for %{name}. Grants the client the access it needs to
the KVMFR shared-memory device under /dev/shm.

%prep
%autosetup -n %{name}-%{upstream_version}

%build
pushd client
%cmake \
    -DENABLE_BACKTRACE=no \
    -DENABLE_X11=no \
    -DENABLE_PULSEAUDIO=no \
    -DENABLE_LIBDECOR=yes \
    .
%cmake_build
popd

%install
mkdir -p %{buildroot}%{_bindir}
cp -a ./client/%{_vpath_builddir}/%{name} %{buildroot}%{_bindir}/.

mkdir -p %{buildroot}%{_datadir}/pixmaps
cp -a ./resources/lg-logo.png %{buildroot}%{_datadir}/pixmaps/%{name}.png

mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/tmpfiles.d/.

desktop-file-install                                    \
--delete-original                                       \
--dir=%{buildroot}%{_datadir}/applications              \
%{SOURCE1}

mkdir -p %{buildroot}%{_datadir}/selinux/packages
mkdir -p selinux_build
cp -a %{SOURCE3} selinux_build/%{selinux_modulename}.te
cp -a %{SOURCE4} selinux_build/%{selinux_modulename}.fc
make -f /usr/share/selinux/devel/Makefile -C selinux_build
cp -a selinux_build/%{selinux_modulename}.pp %{buildroot}%{_datadir}/selinux/packages/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%attr(0755,root,root) %{_bindir}/%{name}
%attr(0644,root,root) %{_datadir}/pixmaps/%{name}.png
%attr(0644,root,root) %{_datadir}/applications/%{name}.desktop
%attr(0644,root,root) %{_sysconfdir}/tmpfiles.d/10-%{name}.conf

%files selinux
%attr(0644,root,root) %{_datadir}/selinux/packages/%{selinux_modulename}.pp

%post
systemd-tmpfiles --create %{_sysconfdir}/tmpfiles.d/10-%{name}.conf || :

%postun
if [ $1 -eq 0 ]; then
    systemd-tmpfiles --remove %{_sysconfdir}/tmpfiles.d/10-%{name}.conf || :
fi

%post selinux
%selinux_modules_install -s targeted %{_datadir}/selinux/packages/%{selinux_modulename}.pp
restorecon -F /dev/shm/looking-glass || :

%postun selinux
if [ $1 -eq 0 ]; then
    %selinux_modules_uninstall -s targeted %{selinux_modulename}
fi

%posttrans selinux
%selinux_relabel_post -s targeted

%changelog
* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 7.0.0-9
- Optimize for Wayland + PipeWire target environment:
  * -DENABLE_X11=no: drop X11/Xrandr/XScrnSaver/xkb-x11 BRs (Wayland-only)
  * -DENABLE_PULSEAUDIO=no: pipewire-pulse shim is enough, drop pulseaudio-libs-devel
  * -DENABLE_LIBDECOR=yes: upstream recommends for GNOME-on-Wayland
- Add BuildRequires: libxkbcommon-devel (for Wayland keyboard), libdecor-devel

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 7.0.0-8
- Disable ENABLE_BACKTRACE to drop libbfd dependency:
  Fedora 44's binutils 2.46 libbfd.a references ZSTD_* symbols but
  binutils-devel doesn't expose libzstd as a link dep, causing link
  failure. Upstream provides ENABLE_BACKTRACE=no as the supported knob.
- Drop unused BuildRequires: binutils-devel

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 7.0.0-7
- Split SELinux policy into looking-glass-client-selinux subpackage
- Use %%selinux_* scriptlet macros (upgrade-safe install/uninstall/relabel)
- Guard %%postun against firing on upgrades

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 7.0.0-6
- Modernize spec: SPDX license, add URL, drop unused SDL2/make BRs
- Switch to %%cmake_build, virtual font provide, normalize Version (B7.0.0 → 7.0.0)
- Add %%check with desktop-file-validate

* Sat Dec 13 2025 Hector Diaz <hdiazc@live.com> - B7.0.0-5
- Fix SE linux module with proper file context and access rules
- Add tmpfiles.d SELinux context application on boot

* Sat Apr 12 2025 Hector Diaz <hdiazc@live.com> - B7.0.0-4
- SE linux module

* Sat Mar 29 2025 Hector Diaz <hdiazc@live.com> - B7.0.0-3
- B7 release

* Sat Jun 29 2024 Hector Diaz <hdiazc@live.com> - B7.0.0-2
- Update to B7-rc1

* Fri Jan 6 2023 Hector Diaz <hdiazc@live.com> - B6.0.0-1
- B6 release

* Sat Feb 26 2022 Hector Diaz <hdiazc@live.com> - B5.0.1-2
- Remote packaged tar.gz

* Sun Feb 13 2022 Hector Diaz <hdiazc@live.com> - B5.0.1-1
- Initial version of the package
