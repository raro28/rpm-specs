Name:           whitesur-gtk-theme
Version:        20250724
Release:        2%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname WhiteSur-gtk-theme
%define dversion 2025-07-24
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

Requires:       gtk-murrine-engine
Requires:       gnome-themes-extra

BuildRequires:  glib2-devel
BuildRequires:  gnome-shell
BuildRequires:  sassc
BuildRequires:  sudo

%description
A macOS like theme for Linux GTK Desktops

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh -t grey -N mojave -l --shell -i gnome --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250724-2
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add Requires: gtk-murrine-engine, gnome-themes-extra (per upstream README)
- Add BuildRequires: gnome-shell (used by --shell install.sh flag)
- Drop spurious BuildRequires: dialog (only used with --dialog/--interactive flags)
- Keep BuildRequires: sudo (lib-core.sh runs `which sudo` at load under set -e)

* Sat Dec 13 2025 Hector Diaz <hdiazc@live.com> - 20250724-1
- Bump version

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250403-2
- Include light

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250403-1
- Bump version

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241118-1
- Initial release