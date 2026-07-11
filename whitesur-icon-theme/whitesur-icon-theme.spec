Name:           whitesur-icon-theme
Version:        20260707
Release:        1%{?dist}
Summary:        A macOS BigSur-like icon theme for Linux desktops
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname WhiteSur-icon-theme
%define dversion 2026-07-07
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires:  gtk-update-icon-cache

%description
A macOS BigSur-like icon theme for Linux desktops.

%prep
%setup -q -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
./install.sh --theme default --alternative --dest "%{buildroot}%{_datarootdir}/icons"

%files
%{_datarootdir}/icons

%changelog
* Sat Jul 11 2026 Hector Diaz <hdiazc@live.com> - 20260707-1
- Bump to upstream 2026-07-07 (install.sh flags unchanged:
  --theme default --alternative --dest)

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20251227-1
- Initial version of the package
