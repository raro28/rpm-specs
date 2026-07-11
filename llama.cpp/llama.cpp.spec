%global build_num       9965
%global upstream_tag    b%{build_num}
# AMD GPU ISA target(s) for the ROCm/HIP backend. gfx1030 = RDNA2 (RX 6800/6900
# XT); Fedora's rocBLAS ships Tensile kernels for it. Add space-separated targets
# here to widen -rocm coverage (each adds build time).
%global amdgpu_targets  gfx1030

Name:           llama.cpp
Version:        0^b%{build_num}
Release:        1%{?dist}
Summary:        LLM inference in C/C++ (CPU engine; GPU backends packaged separately)

# Upstream is MIT. Bundled third-party code under the same or compatible
# permissive terms (see LICENSE and ggml/ for details).
License:        MIT
URL:            https://github.com/ggml-org/llama.cpp

Source0:        https://github.com/ggml-org/llama.cpp/archive/refs/tags/%{upstream_tag}.tar.gz#/llama.cpp-%{upstream_tag}.tar.gz
# Prebuilt SvelteKit web UI bundle (bundle.{css,js}, index.html, loading.html,
# checksums.txt). Released alongside the source tag. Avoids a network fetch
# during %%build which mock blocks by default.
Source1:        https://github.com/ggml-org/llama.cpp/releases/download/%{upstream_tag}/llama-%{upstream_tag}-ui.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  pkgconf-pkg-config
# Vulkan backend
BuildRequires:  vulkan-loader-devel
BuildRequires:  vulkan-headers
BuildRequires:  glslc
BuildRequires:  glslang
BuildRequires:  spirv-headers-devel
# ROCm/HIP backend (compiles the gfx1030 device kernels; no GPU needed to build)
BuildRequires:  rocm-hip-devel
BuildRequires:  hipblas-devel
BuildRequires:  rocblas-devel
BuildRequires:  rocm-comgr-devel
BuildRequires:  rocm-cmake
BuildRequires:  clang
BuildRequires:  llvm
# common
BuildRequires:  libcurl-devel
# Activates LLAMA_OPENSSL (default ON): HTTPS support in the server's httplib client.
BuildRequires:  openssl-devel

# Base is the CPU engine + shared binaries; GPU acceleration is delivered by the
# -vulkan / -rocm backend subpackages, each a single dlopen module ggml discovers
# at runtime. Recommend the portable Vulkan backend so a bare `dnf install
# llama.cpp` stays GPU-accelerated by default (weak dep: droppable on CPU-only hosts).
Recommends:     %{name}-vulkan = %{version}-%{release}

%description
llama.cpp is a plain-C/C++ implementation of LLM inference with minimal
dependencies, supporting GGUF model files. This base package provides the CPU
inference engine (every x86-64 micro-architecture variant, runtime-dispatched)
and the shared binaries: llama-cli, llama-server, llama-bench, llama-quantize,
llama-tokenize, and friends.

GPU acceleration is optional and delivered by separate backend packages that
ggml loads at runtime when installed:
  * llama.cpp-vulkan -- portable Vulkan backend (Mesa RADV/ANV, NVIDIA)
  * llama.cpp-rocm   -- AMD ROCm/HIP backend (gfx1030 / RDNA2)

%package vulkan
Summary:        Vulkan GPU backend for llama.cpp
Requires:       %{name} = %{version}-%{release}
# Runtime needs a Vulkan ICD. On AMD/Intel that's Mesa's RADV/ANV
# (mesa-vulkan-drivers); on NVIDIA the proprietary driver provides one.
Recommends:     mesa-vulkan-drivers

%description vulkan
Vulkan compute backend for llama.cpp (libggml-vulkan.so). Runs on any GPU with a
Vulkan driver -- Mesa RADV/ANV for AMD/Intel, NVIDIA's proprietary driver. ggml
discovers and loads it at runtime; install alongside the llama.cpp base package.
Portable across GPU vendors.

%package rocm
Summary:        ROCm/HIP GPU backend for llama.cpp (AMD gfx1030)
Requires:       %{name} = %{version}-%{release}

%description rocm
ROCm/HIP compute backend for llama.cpp (libggml-hip.so), compiled for AMD
gfx1030 (RDNA2 -- e.g. Radeon RX 6800/6800 XT/6900 XT). Pulls in rocBLAS and
hipBLAS. ggml discovers and loads it at runtime; install alongside the llama.cpp
base package. AMD-only and specific to the gfx1030 target.

%prep
%autosetup -n llama.cpp-%{upstream_tag}
# Stage prebuilt UI assets so scripts/ui-assets.cmake picks them up via its
# "assets already present" branch and skips the HF download (mock is offline).
mkdir -p tools/ui/dist
tar xf %{SOURCE1} --strip-components=1 -C tools/ui/dist

%build
# One pass builds all three backends as GGML_BACKEND_DL dlopen modules:
# libggml-cpu-*.so (base), libggml-vulkan.so (-vulkan), libggml-hip.so (-rocm).
%cmake \
    -DGGML_VULKAN=ON \
    -DGGML_HIP=ON \
    -DAMDGPU_TARGETS=%{amdgpu_targets} \
    -DGGML_NATIVE=OFF \
    -DGGML_LTO=ON \
    -DGGML_BACKEND_DL=ON \
    -DGGML_CPU_ALL_VARIANTS=ON \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_USE_PREBUILT_UI=ON \
    -DLLAMA_BUILD_NUMBER=%{build_num} \
    -DLLAMA_CURL=ON \
    -DLLAMA_OPENSSL=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_LIBDIR=%{_lib}
%cmake_build

%install
%cmake_install
# Runtime-only package: drop dev artifacts (headers, bare .so symlinks, pkgconfig,
# cmake). Versioned sonames and the private impl libs stay.
rm -rf %{buildroot}%{_includedir} %{buildroot}%{_libdir}/cmake
rm -f  %{buildroot}%{_libdir}/pkgconfig/*.pc
find %{buildroot}%{_libdir} -maxdepth 1 -type l -name '*.so' -delete

%check
test -x %{buildroot}%{_bindir}/llama-cli
test -x %{buildroot}%{_bindir}/llama-server
test -x %{buildroot}%{_bindir}/llama-bench
# All three backends must have built as their own dlopen modules:
test -f %{buildroot}%{_bindir}/libggml-vulkan.so
test -f %{buildroot}%{_bindir}/libggml-hip.so
ls %{buildroot}%{_bindir}/libggml-cpu-*.so >/dev/null

%files
%license LICENSE
%doc README.md
%{_bindir}/llama
%{_bindir}/llama-*
# CPU backend modules land in _bindir (not _libdir) with GGML_BACKEND_DL=ON so
# the main binaries dlopen them via $ORIGIN-relative search. GPU backend modules
# ship in the -vulkan / -rocm subpackages.
%{_bindir}/libggml-cpu-*.so
%{_libdir}/libllama*.so.*
%{_libdir}/libggml*.so.*
%{_libdir}/libmtmd.so.*
# Private impl libs (sonameless regular files, runtime-NEEDED by the launchers).
%{_libdir}/libllama-*-impl.so

%files vulkan
%license LICENSE
%{_bindir}/libggml-vulkan.so

%files rocm
%license LICENSE
%{_bindir}/libggml-hip.so

%changelog
* Sat Jul 11 2026 Hector Diaz <hdiazc@live.com> - 0^b9965-1
- Rebase to upstream tag b9965 (137 builds from b9828). Build-option surface
  verified unchanged against the b9828..b9965 CMake source: root CMakeLists has
  no option diff; ggml only bumped its version and added the OFF-by-default
  GGML_ET backend (unused). All existing flags behave the same.
- Split into backend subpackages using the existing GGML_BACKEND_DL layout, built
  in one pass (-DGGML_VULKAN=ON -DGGML_HIP=ON):
  * llama.cpp (base): binaries + core libs + the CPU backend (all x86-64
    variants). No GPU dependency. Recommends %%{name}-vulkan so a default install
    stays GPU-accelerated.
  * llama.cpp-vulkan: the libggml-vulkan.so dlopen module (NEEDED: libvulkan);
    Recommends mesa-vulkan-drivers.
  * llama.cpp-rocm: the libggml-hip.so dlopen module built for
    AMDGPU_TARGETS=gfx1030 (NEEDED: rocblas/hipblas/amdhip64).
  The three modules coexist; ggml loads whichever are installed and enumerates
  all their devices. Verified from the built artifacts that each backend module
  NEEDs only its own GPU stack and the core/binaries carry no GPU linkage, so
  RPM's soname-based dep generation isolates rocBLAS to -rocm and Vulkan to
  -vulkan automatically.
- Add the ROCm/HIP build toolchain to BuildRequires (rocm-hip-devel,
  hipblas-devel, rocblas-devel, rocm-comgr-devel, rocm-cmake, clang, llvm). The
  gfx1030 kernels compile ahead-of-time from the ISA string; no GPU is needed at
  build time (proven in a GPU-less mock chroot).
- NOTE: -rocm is build-verified only. Its gfx1030 target (RX 6900 XT) is bound to
  vfio-pci on the build host, so runtime performance is not yet measured;
  Vulkan-vs-ROCm benchmarking is deferred until the card is available to the host.

* Sat Jun 27 2026 Hector Diaz <hdiazc@live.com> - 0^b9828-1
- Rebase to upstream tag b9828 (284 commits from b9544). Pure version bump;
  build flags verified unchanged against the b9828 CMake source.
- Add BuildRequires: openssl-devel and pass -DLLAMA_OPENSSL=ON to compile HTTPS
  into the server's httplib client (default-ON option, previously inert without
  openssl headers). Client-only; no certificate required.
- Drop link-time dev artifacts (headers, bare .so symlinks, pkgconfig, cmake):
  runtime-only inference package, nothing builds against libllama. Clears the
  devel-file-in-non-devel-package warnings without a -devel subpackage. Versioned
  sonames and the private impl libs are retained. Binary RPM now lints 0/0 (the
  unfixable upstream invalid-soname/no-manual-page/cli items are filtered with
  documented rationale in rpmlint.toml).

* Sat Jun 06 2026 Hector Diaz <hdiazc@live.com> - 0^b9544-1
- Rebase to upstream tag b9544 (239 commits from b9305). Pure version bump:
  verified against the b9305..b9544 diff that no spec logic changes are needed.
  * All build flags still exist and behave the same: GGML_VULKAN, GGML_NATIVE,
    GGML_LTO, GGML_BACKEND_DL, GGML_CPU_ALL_VARIANTS (still gated on
    BACKEND_DL), LLAMA_BUILD_SERVER, LLAMA_USE_PREBUILT_UI (still default ON),
    LLAMA_BUILD_NUMBER, BUILD_SHARED_LIBS.
  * UI staging path unchanged: scripts/ui-assets.cmake Priority 1 still copies
    pre-built assets from tools/ui/dist before any network fetch (only change
    upstream was npm-install staleness detection, which we don't hit). The
    llama-b9544-ui.tar.gz release asset (Source1) exists.
  * Installed file layout unchanged; the unified "llama-app" binary already
    existed at b9305 and is covered by the %%{_bindir}/llama-* glob.
- Note: -DLLAMA_CURL=ON now emits a "deprecated and will be ignored" warning,
  but this is pre-existing (already deprecated at b9305) — curl is auto-enabled
  when libcurl-devel is present, so -hf downloads still work. Harmless; left as
  documentation of intent.

* Sun May 24 2026 Hector Diaz <hdiazc@live.com> - 0^b9305-4
- Enable GGML_BACKEND_DL=ON + GGML_CPU_ALL_VARIANTS=ON so the CPU backend
  ships every x86_64 instruction variant (sse42, x64, sandybridge, ivybridge,
  haswell, skylakex, icelake, cascadelake, cooperlake, cannonlake, alderlake,
  sapphirerapids, zen4, piledriver) as separate dlopen-loaded .so files.
  Runtime dispatcher picks the best one for the host CPU - the same RPM is
  fast on a 5950X (zen4-class avx2/fma) and still loads on older boxes
  without it. The two flags are coupled by upstream (ggml/CMakeLists.txt:183,
  "requires GGML_BACKEND_DL").
- Add %%{_bindir}/libggml-*.so to %%files: with GGML_BACKEND_DL=ON upstream
  installs the dlopen'd backend libs (libggml-cpu-*.so, libggml-vulkan.so)
  under bindir, not libdir, so main binaries find them via $ORIGIN.
- Keep -DLLAMA_USE_PREBUILT_UI=ON pinned explicitly even though it's the
  current upstream default (CMakeLists.txt:113). Defaults drift between
  releases and a future b9XXX flipping it to OFF would silently regress
  our UI bundling path.

* Sun May 24 2026 Hector Diaz <hdiazc@live.com> - 0^b9305-3
- Stage the prebuilt UI bundle as Source1 (the llama-bNNNN-ui.tar.gz asset
  from the matching GitHub release) and extract into tools/ui/dist during
  %%prep. The -2 build set LLAMA_USE_PREBUILT_UI=ON but mock disables network
  during %%build so the HF download from scripts/ui-assets.cmake silently
  failed and the server was built with no embedded UI (404 at /). With the
  bundle pre-staged the cmake "assets already present" branch wins before
  any network is attempted.

* Sun May 24 2026 Hector Diaz <hdiazc@live.com> - 0^b9305-2
- Enable web UI: pass -DLLAMA_USE_PREBUILT_UI=ON and -DLLAMA_BUILD_NUMBER
  so tools/ui/CMakeLists.txt fetches the prebuilt SvelteKit bundle from
  HuggingFace at the matching b9305 version and embeds it via
  llama-ui-embed (avoids pulling in nodejs + npm as build deps to build
  the UI from source).

* Sun May 24 2026 Hector Diaz <hdiazc@live.com> - 0^b9305-1
- Initial package: llama.cpp upstream tag b9305, Vulkan backend enabled.
- Pin GGML_NATIVE=OFF for portable binaries (same class of fix as
  OPTIMIZE_FOR_NATIVE=x86-64-v3 on looking-glass-client: avoid baking
  the COPR builder's CPU instructions into the RPM).
- Build with LLAMA_CURL=ON so `-hf user/repo` model downloads work.
- Fedora versioning: Version=0^b9305 (caret = post-release snapshot;
  the project has no upstream semver, only bNNNN build-number tags).
- BuildRequires glslang + spirv-headers in addition to glslc — upstream's
  Vulkan CMake module pulls in SPIRV-HeadersConfig.cmake at configure
  time and runs glslangValidator alongside glslc during shader compile.
