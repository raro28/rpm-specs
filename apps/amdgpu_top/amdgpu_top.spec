%global forgeurl https://github.com/Umio-Yasuno/%{name}
%global appid    io.github.umio_yasuno.%{name}

Name:           amdgpu_top
Version:        0.11.5
Release:        1%{?dist}
Summary:        Tool to display AMD GPU usage

# Upstream is MIT. The GUI front end embeds the BIZ UDGothic font, which is OFL-1.1.
License:        MIT AND OFL-1.1
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExclusiveArch:  %{rust_arches}

# Edition 2024 needs rustc >= 1.85; F44 ships 1.98.
BuildRequires:  cargo
BuildRequires:  rust >= 1.85
BuildRequires:  gcc
# libdrm_amdgpu_sys is built with its link_drm feature: it links -ldrm and
# -ldrm_amdgpu instead of dlopen()ing them, so the headers are needed here.
BuildRequires:  pkgconfig(libdrm)
# %%check validators only.
BuildRequires:  desktop-file-utils
BuildRequires:  appstream

%description
amdgpu_top reports AMD GPU utilization from the GPU performance counters (GRBM,
GRBM2), sensors, fdinfo, gpu_metrics and the amdgpu kernel driver. It has a TUI
mode (the default), an SMI mode (--smi), a GUI mode (--gui), JSON output
(--json) and a one-shot device dump (-d).

%prep
%autosetup -n %{name}-%{version}

%build
# Crates are fetched from crates.io during the build. They are not vendored and
# cannot come from Fedora's rust-* packages: libdrm_amdgpu_sys is pinned to a git
# revision, not a crates.io release. --locked holds every crate to the exact
# version and checksum recorded in Cargo.lock, so the build stays reproducible.
# Build locally with `mock --enable-network`; the COPR has enable_net set.
%{?build_rustflags:export RUSTFLAGS="%{build_rustflags}"}
# `package` is upstream's own packaging feature: libdrm_link, tui, gui, json.
# It omits git_version, which reads a .git this tarball does not carry.
cargo build --release --locked \
    %{?_smp_build_ncpus:-j%{_smp_build_ncpus}} \
    --no-default-features --features package

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 docs/%{name}.1 %{buildroot}%{_mandir}/man1/%{name}.1
install -Dpm 0644 assets/%{name}.desktop \
    %{buildroot}%{_datadir}/applications/%{name}.desktop
install -Dpm 0644 assets/%{name}-tui.desktop \
    %{buildroot}%{_datadir}/applications/%{name}-tui.desktop
install -Dpm 0644 assets/%{appid}.metainfo.xml \
    %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}-tui.desktop
appstreamcli validate --no-net %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

%files
%license LICENSE
%license crates/amdgpu_top_gui/fonts/LICENSE_BIZUDGothic
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/applications/%{name}-tui.desktop
%{_metainfodir}/%{appid}.metainfo.xml

%changelog
* Sat Sep 05 2026 Hector Diaz <hdiazc@live.com> - 0.11.5-1
- Initial package
