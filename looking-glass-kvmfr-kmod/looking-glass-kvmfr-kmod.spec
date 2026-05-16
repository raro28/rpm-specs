%global buildforkernels akmod
%global debug_package    %{nil}

# Pulled in as Requires on akmod-<name> via kmodtool, so that akmodsbuild
# on the user's machine has the same BR set as the COPR/mock build.
%global AkmodsBuildRequires kernel-rpm-macros systemd-rpm-macros gcc make elfutils-libelf-devel

%global upstream_tag     B7
%global kmod_name        kvmfr
%global mod_workdir      %{kmod_name}-%{version}

Name:           looking-glass-kvmfr-kmod
Summary:        Looking Glass KVMFR shared-memory kernel module (akmod)
Version:        0.0.12
Release:        5%{?dist}
License:        GPL-2.0-or-later

URL:            https://looking-glass.io/

Source0:        https://github.com/gnif/LookingGlass/archive/refs/tags/%{upstream_tag}.tar.gz#/LookingGlass-%{upstream_tag}.tar.gz
Source1:        kvmfr.conf
Source2:        99-kvmfr.rules

Patch0:         0001-add-module-description.patch

# Build-time deps. With buildforkernels=akmod no .ko is compiled during
# SRPM/COPR build; the per-kernel rebuild happens on the user's machine
# via the akmods service. The toolchain BRs are only needed when someone
# overrides `--define 'kernels=...'` to bake fixed-kernel kmods at SRPM
# build time (typically done by RPMFusion-style CI, not by COPR).
BuildRequires:  kmodtool
BuildRequires:  systemd-rpm-macros
BuildRequires:  kernel-rpm-macros
%{?kernels:BuildRequires: kernel-devel}
%{?kernels:BuildRequires: gcc}
%{?kernels:BuildRequires: make}
%{?kernels:BuildRequires: elfutils-libelf-devel}

# kmodtool emits akmod-<name> + kmod-<name> (meta) subpackage stubs.
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null)}

%description
The kvmfr ("KVM Frame Relay") kernel module exposes a character device
(/dev/kvmfr0) backed by shared memory for use with Looking Glass. It
provides DMA-BUF support for zero-copy GPU frame transfers between a host
and a guest using PCI passthrough, replacing the older /dev/shm IVSHMEM
file-backed approach.

This package ships the akmod scaffolding: source for the kernel module
plus the akmods service plumbing that rebuilds and installs the .ko
against whichever kernel(s) you have installed, and re-runs automatically
on every kernel update.

%package -n %{kmod_name}-kmod-common
Summary:        Runtime configuration for the kvmfr kernel module
BuildArch:      noarch
Requires:       systemd
Requires(post): systemd
Recommends:     looking-glass-client

%description -n %{kmod_name}-kmod-common
Modprobe options and udev rules shared by all kmod-kvmfr-<kernel>
packages and required by akmod-kvmfr:
 - %{_modprobedir}/kvmfr.conf       (sets static_size_mb=256)
 - %{_udevrulesdir}/99-kvmfr.rules  (gives /dev/kvmfr0 to group kvm)

%prep
%{?kmodtool_check}
%setup -q -c -T -a 0
pushd LookingGlass-%{upstream_tag}
%patch -P 0 -p1
popd
mv LookingGlass-%{upstream_tag}/module   %{mod_workdir}
mv LookingGlass-%{upstream_tag}/LICENSE  %{mod_workdir}/LICENSE
rm -rf LookingGlass-%{upstream_tag}

for kernel_version in %{?kernel_versions} ; do
    cp -a %{mod_workdir} _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions} ; do
    make %{?_smp_mflags} \
         -C ${kernel_version##*___} \
         M=${PWD}/_kmod_build_${kernel_version%%___*} modules
done

%install
for kernel_version in %{?kernel_versions} ; do
    install -D -m 644 _kmod_build_${kernel_version%%___*}/%{kmod_name}.ko \
        %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/%{kmod_name}.ko
done

install -D -m 644 %{SOURCE1} %{buildroot}%{_modprobedir}/%{kmod_name}.conf
install -D -m 644 %{SOURCE2} %{buildroot}%{_udevrulesdir}/99-%{kmod_name}.rules

%{?akmod_install}

%post -n %{kmod_name}-kmod-common
udevadm control --reload-rules || :
udevadm trigger --subsystem-match=kvmfr || :

%files -n %{kmod_name}-kmod-common
%license %{mod_workdir}/LICENSE
%{_modprobedir}/%{kmod_name}.conf
%{_udevrulesdir}/99-%{kmod_name}.rules

%changelog
* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 0.0.12-5
- Polish:
  * Move toolchain BRs (gcc, make, elfutils-libelf-devel, kernel-devel)
    behind %%{?kernels:...} — they're only needed when baking fixed-kernel
    kmods at SRPM build time; COPR's akmod-only path doesn't compile
  * Ship upstream LICENSE via %%license
  * Recommends: looking-glass-client on kvmfr-kmod-common
  * Add udevadm trigger to %%post so /dev/kvmfr0 perms apply immediately if
    the module is already loaded
  * Expand %%description with what akmods does for the user

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 0.0.12-4
- Set AkmodsBuildRequires so akmod-kvmfr pulls in the build deps that
  akmodsbuild needs on the user's machine (kernel-rpm-macros,
  systemd-rpm-macros, gcc, make, elfutils-libelf-devel)

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 0.0.12-3
- Rename config subpackage to kvmfr-kmod-common (the exact name kmodtool's
  --akmod path expects via `Requires: kvmfr-kmod-common`). Single install
  transaction now satisfies the akmod's dep chain.

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 0.0.12-2
- Fix path macro expansion: add systemd-rpm-macros + kernel-rpm-macros BRs
  (_modprobedir/_udevrulesdir come from systemd-rpm-macros)
- Replace the bogus %%{?kmod_filelist} echo trick with an explicit
  config subpackage owning the modprobe.d/udev files
- Use modern %%patch -P 0 -p1 spacing
- Run `udevadm control --reload-rules` on config install

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 0.0.12-1
- Initial packaging of the kvmfr kernel module (extracted from LookingGlass B7)
- Patch: add MODULE_DESCRIPTION to silence modpost warning
