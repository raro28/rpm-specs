Name:           scream
Version:        3.9
Release:        1%{?dist}
Summary:        Audio receiver using Pulseaudio, ALSA or stdout as audio output

License:        MS-PL
Source0:        %{name}-%{version}.tar.gz

BuildRequires:       gcc
BuildRequires:       binutils-devel
BuildRequires:       cmake
BuildRequires:       make
BuildRequires:       pkgconf-pkg-config
BuildRequires:       pulseaudio-libs-devel
BuildRequires:       alsa-lib-devel


%description
Scream is a Scream audio receiver using Pulseaudio, 
ALSA or stdout as audio output.

%prep
%autosetup

%build
mkdir ./Receivers/unix/build
pushd Receivers/unix/build
%cmake ../
pushd redhat-linux-build
make -j`nproc`
popd
popd

%install
mkdir -p %{buildroot}%{_bindir}
cp -a ./Receivers/unix/build/redhat-linux-build/%{name} %{buildroot}%{_bindir}/.

%files
%attr(0755,root,root) %{_bindir}/%{name}

%changelog
* Sun Feb 13 2022 Hector Diaz <hdiazc@live.com> - 3.9-1
- Initial version of the package