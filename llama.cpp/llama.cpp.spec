%global build_num     9544
%global upstream_tag  b%{build_num}

Name:           llama.cpp
Version:        0^b%{build_num}
Release:        1%{?dist}
Summary:        LLM inference in C/C++ (Vulkan-accelerated build)

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
BuildRequires:  vulkan-loader-devel
BuildRequires:  vulkan-headers
BuildRequires:  glslc
BuildRequires:  glslang
BuildRequires:  spirv-headers-devel
BuildRequires:  libcurl-devel

Requires:       vulkan-loader
# Runtime needs a Vulkan ICD. On AMD/Intel that's Mesa's RADV/ANV
# (mesa-vulkan-drivers); on NVIDIA the proprietary driver provides one.
Recommends:     mesa-vulkan-drivers

%description
llama.cpp is a plain-C/C++ implementation of LLM inference with minimal
dependencies, supporting GGUF model files. This package ships the
Vulkan-accelerated build, which runs on any GPU with a Vulkan driver
(Mesa RADV for AMD/Intel, NVIDIA's proprietary driver).

Includes the standard binaries: llama-cli, llama-server, llama-bench,
llama-quantize, llama-tokenize, and friends.

%prep
%autosetup -n llama.cpp-%{upstream_tag}
# Stage prebuilt UI assets so scripts/ui-assets.cmake picks them up via its
# "assets already present" branch and skips the HF download (mock is offline).
mkdir -p tools/ui/dist
tar xf %{SOURCE1} --strip-components=1 -C tools/ui/dist

%build
%cmake \
    -DGGML_VULKAN=ON \
    -DGGML_NATIVE=OFF \
    -DGGML_LTO=ON \
    -DGGML_BACKEND_DL=ON \
    -DGGML_CPU_ALL_VARIANTS=ON \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_USE_PREBUILT_UI=ON \
    -DLLAMA_BUILD_NUMBER=%{build_num} \
    -DLLAMA_CURL=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_LIBDIR=%{_lib}
%cmake_build

%install
%cmake_install

%check
test -x %{buildroot}%{_bindir}/llama-cli
test -x %{buildroot}%{_bindir}/llama-server
test -x %{buildroot}%{_bindir}/llama-bench

%files
%license LICENSE
%doc README.md
%{_bindir}/llama
%{_bindir}/llama-*
# Backend libs land in _bindir (not _libdir) with GGML_BACKEND_DL=ON so the
# main binaries can dlopen them via $ORIGIN-relative search.
%{_bindir}/libggml-*.so
%{_libdir}/libllama*.so*
%{_libdir}/libggml*.so*
%{_libdir}/libmtmd.so*
%{_includedir}/*.h
%{_libdir}/cmake/ggml/
%{_libdir}/cmake/llama/
%{_libdir}/pkgconfig/*.pc

%changelog
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
