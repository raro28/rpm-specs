# Upstream's last tag (2025-07-24) predates GNOME 49/50. We build from a pinned
# master snapshot that carries upstream's own "Fixed gnome 50 issues" work
# (the $GNOME_SHELL version-gating mechanism + quick-settings fix), plus a
# downstream patch for the new GNOME 50 login selectors. Refresh %%commit to
# advance; switch back to a tag once upstream cuts a release with 49/50 support.
%global commit       a83f467e4c16b1ed1c960f3d89e2472d9639477c
%global shortcommit  %(c=%{commit}; echo ${c:0:7})

Name:           whitesur-gtk-theme
# Date-versioned to supersede the installed 20250724 build. Today's date sorts
# below any future upstream YYYYMMDD tag (all dated after today), so real
# upstream updates still win. dname-shortcommit identifies the actual source.
Version:        20260606
Release:        1%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname WhiteSur-gtk-theme
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/%{commit}.tar.gz#/%{dname}-%{shortcommit}.tar.gz
# Downstream: style the new GNOME 50 login nodes (.a11y-button gains WhiteSur's
# system-button look; .login-dialog-bottom-button-group spacing). Additive only
# — these selectors don't exist pre-50, so the rules are inert on older shells.
Patch0:         gnome50-login-selectors.patch

BuildRequires:  glib2-devel
BuildRequires:  gnome-shell
BuildRequires:  sassc
BuildRequires:  sudo

%description
A macOS like theme for Linux GTK Desktops

%prep
%autosetup -p1 -n %{dname}-%{commit}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh -t grey -N mojave -l --shell -i gnome --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sat Jun 06 2026 Hector Diaz <hdiazc@live.com> - 20260606-1
- Rebase onto a pinned upstream master snapshot (commit a83f467e, 2026-05-25),
  50 commits past the last tag (2025-07-24). This pulls in upstream's own
  "Fixed gnome 50 issues" work — the $GNOME_SHELL version-gating mechanism and
  the quick-settings margin fix — plus ~9 months of GTK4/app-theming bugfixes
  (firefox 143, nautilus, gdm, _common-4.0.scss) relevant on GNOME 50.
- Add Patch0 (gnome50-login-selectors.patch): style the new GNOME 50 login
  screen nodes. .a11y-button is added to WhiteSur's system-button selector
  groups so the accessibility button matches its siblings; the new
  .login-dialog-bottom-button-group gets gnome-shell's own 32px/16px spacing.
  Additive only — inert on GNOME < 50.
- Version bumped to today's date (20260606) so this supersedes the installed
  20250724 build while staying below any future upstream YYYYMMDD tag.
- NOTE: the GNOME Shell theme still tops out at upstream's widgets-48-0 (clamped
  for shells >= 48); it renders on GNOME 50 but is not pixel-native there, and
  requires the user-theme GNOME Shell extension. Visual correctness on a live
  GNOME 50 session is unverified by the build.

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
