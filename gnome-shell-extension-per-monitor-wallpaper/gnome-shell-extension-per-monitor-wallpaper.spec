%global srcname per-monitor-wallpaper
%global uuid    per-monitor-wallpaper@ekthor

Name:           gnome-shell-extension-per-monitor-wallpaper
Version:        1.0.2
Release:        1%{?dist}
Summary:        GNOME Shell extension that paints each monitor its own wallpaper
BuildArch:      noarch

License:        GPL-3.0-or-later
URL:            https://github.com/raro28/%{srcname}
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz

# Pure GJS; nothing is compiled, so there are no BuildRequires.

# The extension declares shell-version ["50"] and shell extensions break across
# GNOME major versions, so pin to the 50.x series.
Requires:       (gnome-shell >= 50 with gnome-shell < 51)
# Reads the org.gnome.desktop.background schema.
Requires:       gsettings-desktop-schemas

%description
A minimal GNOME Shell extension that paints each monitor its own wallpaper, read
from ~/.config/per-monitor-wallpaper/config.json. It works where GNOME's spanned
wallpaper cannot tile (mixed-resolution / rotated monitors); any tool, or you by
hand, can write the config.

Installed system-wide. Enable it per user with:
    gnome-extensions enable %{uuid}

%prep
%autosetup -n %{srcname}-%{version}

%build
# Nothing to build.

%install
install -d %{buildroot}%{_datadir}/gnome-shell/extensions/%{uuid}
install -pm 0644 src/metadata.json src/extension.js \
    %{buildroot}%{_datadir}/gnome-shell/extensions/%{uuid}/

%files
%license LICENSE
%doc README.md
%{_datadir}/gnome-shell/extensions/%{uuid}/

%changelog
* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 1.0.2-1
- Fix secondary monitors going unpainted (windows smear): assert the
  background actor is visible whenever the extension paints it

* Thu Jun 18 2026 Hector Diaz <hdiazc@live.com> - 1.0.1-1
- Correct README config example: drop the unused per-monitor "mode" key and a
  nonexistent monitor-listing command

* Thu Jun 18 2026 Hector Diaz <hdiazc@live.com> - 1.0.0-1
- Initial package
