%global srcname per-monitor-wallpaper
%global uuid    per-monitor-wallpaper@ekthor

Name:           gnome-shell-extension-per-monitor-wallpaper
Version:        2.1.0
Release:        1%{?dist}
Summary:        GNOME Shell extension that paints each monitor its own wallpaper
BuildArch:      noarch

License:        GPL-3.0-or-later
URL:            https://github.com/raro28/%{srcname}
Source0:        %{url}/releases/download/v%{version}/per-monitor-wallpaper-%{version}.tar.gz

# Authored in TypeScript, built by CI into the release tarball; the RPM
# compiles nothing and needs no BuildRequires.

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
%autosetup -n %{uuid}

%build
# Nothing to build.

%install
install -d %{buildroot}%{_datadir}/gnome-shell/extensions/%{uuid}
install -pm 0644 metadata.json extension.js prefs.js \
    %{buildroot}%{_datadir}/gnome-shell/extensions/%{uuid}/

%files
%license LICENSE
%doc README.md
%{_datadir}/gnome-shell/extensions/%{uuid}/

%changelog
* Mon Jun 22 2026 Hector Diaz <hdiazc@live.com> - 2.1.0-1
- Add preferences UI (per-monitor wallpaper + fit-mode preview); honor the config "mode" field

* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 2.0.0-1
- Port to TypeScript/esbuild; Source0 is now the CI-built release tarball (no behavior change)

* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 1.0.2-1
- Fix secondary monitors going unpainted (windows smear): assert the
  background actor is visible whenever the extension paints it

* Thu Jun 18 2026 Hector Diaz <hdiazc@live.com> - 1.0.1-1
- Correct README config example: drop the unused per-monitor "mode" key and a
  nonexistent monitor-listing command

* Thu Jun 18 2026 Hector Diaz <hdiazc@live.com> - 1.0.0-1
- Initial package
