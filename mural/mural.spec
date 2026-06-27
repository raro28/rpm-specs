Name:           mural
Version:        1.0.0
Release:        1%{?dist}
Summary:        Per-monitor wallpaper editor (GTK4/libadwaita)
BuildArch:      noarch

License:        GPL-3.0-or-later
URL:            https://github.com/raro28/%{name}
Source0:        %{url}/releases/download/v%{version}/%{name}-%{version}.tar.gz
# Man page maintained downstream (upstream ships none).
Source1:        %{name}.1

# Authored in TypeScript, built by CI into the release tarball; the RPM compiles
# nothing. BuildRequires are for %%check (validators) only.
BuildRequires:  desktop-file-utils
BuildRequires:  appstream

# GJS runtime + GTK4/libadwaita stack.
Requires:       gjs
Requires:       gtk4
Requires:       libadwaita
# Thumbnail decode: Glycin (Gly + GlyGtk4 typelibs) and its image-format loaders.
Requires:       glycin-libs
Requires:       glycin-gtk4-libs
Requires:       glycin-loaders
# Owns /usr/share/icons/hicolor.
Requires:       hicolor-icon-theme

%description
Mural assigns a wallpaper and fit mode to each connected monitor, writing
~/.config/per-monitor-wallpaper/config.json. It shows a to-scale arrangement
of the connected displays; pick an image per monitor and a fit mode (zoom,
fill, fit, or center). Changes are written immediately.

Mural is the standalone editor for the config that the per-monitor-wallpaper
GNOME Shell extension reads. It is an ordinary GTK client and does not run
inside gnome-shell.

%prep
%autosetup

%build
# Nothing to build (prebuilt bundle).

%install
install -Dpm 0755 bin/mural %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 mural.js %{buildroot}%{_datadir}/%{name}/mural.js
install -Dpm 0644 data/dev.muy.Mural.desktop %{buildroot}%{_datadir}/applications/dev.muy.Mural.desktop
install -Dpm 0644 data/dev.muy.Mural.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/dev.muy.Mural.svg
install -Dpm 0644 data/dev.muy.Mural.metainfo.xml %{buildroot}%{_metainfodir}/dev.muy.Mural.metainfo.xml
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_mandir}/man1/%{name}.1

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/dev.muy.Mural.desktop
appstreamcli validate --no-net %{buildroot}%{_metainfodir}/dev.muy.Mural.metainfo.xml

%files
%doc README.md
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/dev.muy.Mural.desktop
%{_datadir}/icons/hicolor/scalable/apps/dev.muy.Mural.svg
%{_metainfodir}/dev.muy.Mural.metainfo.xml
%{_mandir}/man1/%{name}.1*

%changelog
* Sat Jun 27 2026 Hector Diaz <hdiazc@live.com> - 1.0.0-1
- Initial package
