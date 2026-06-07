Name:           whitesur-gtk-theme
Version:        20250724
Release:        4%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname WhiteSur-gtk-theme
%define dversion 2025-07-24
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires:  glib2-devel
BuildRequires:  gnome-shell
BuildRequires:  sassc
BuildRequires:  sudo

%description
A macOS like theme for Linux GTK Desktops

%prep
%setup -q -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh -t grey -N mojave -l --shell -i gnome --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250724-4
- Drop GTK2-era runtime deps (adwaita-gtk2-theme, gtk-murrine-engine):
  adwaita-gtk2-theme was removed from Fedora 44 repos, and the gtk-2.0/
  payload only matters for legacy GTK2 apps

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250724-3
- Replace gnome-themes-extra dep with Fedora's adwaita-gtk2-theme
  (libs/lib-install.sh installs gtk-2.0 theme that inherits Adwaita)

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
