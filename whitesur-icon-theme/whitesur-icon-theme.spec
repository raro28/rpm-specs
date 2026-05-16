Name:           whitesur-icon-theme
Version:        20251227
Release:        1%{?dist}
Summary:        A macOS BigSur-like icon theme for Linux desktops
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname WhiteSur-icon-theme
%define dversion 2025-12-27
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires:  gtk-update-icon-cache

%description
A macOS BigSur-like icon theme for Linux desktops.

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
./install.sh --theme default --alternative --dest "%{buildroot}%{_datarootdir}/icons"

%files
%{_datarootdir}/icons

%changelog
* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20251227-1
- Initial version of the package
