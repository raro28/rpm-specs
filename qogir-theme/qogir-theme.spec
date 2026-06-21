Name:           qogir-theme
Version:        20250817
Release:        5%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Qogir-theme
%define dversion 2025-08-17
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz
Patch0:         gnome50-selectors.patch
Patch1:         gnome50-appearance.patch

BuildRequires:  gnome-shell
BuildRequires:  sassc
# %%check: validate the compiled GTK4 CSS with the real GTK engine
BuildRequires:  gtk4
BuildRequires:  python3-gobject-base

%description
Qogir is a flat Design theme for GTK 3, GTK 2 
and Gnome-Shell which supports GTK 3 and GTK 2 
based desktop environments like Gnome, Unity, Budgie, 
Cinnamon Pantheon, XFCE, Mate, etc

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh --icon gnome --tweaks round --libadwaita --dest %{buildroot}%{_datarootdir}/themes

%check
# GTK 4.x build-time test: parse every installed gtk-4.0 stylesheet through the
# real GTK CSS engine (GtkCssProvider) and fail on any genuine syntax error. The
# benign base-resource @import ("resource:///org/gnome/theme/...") is ignored: it
# only resolves at runtime inside a GTK application, not when linting standalone.
python3 - <<'PYEOF'
import gi, sys, glob
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
real = 0
cur = ""
def on_err(prov, section, err):
    global real
    if "does not exist" in err.message:
        return
    loc = section.get_start_location()
    sys.stderr.write("CSS ERROR " + cur + ":" + str(loc.lines + 1) + ": " + err.message + "\n")
    real += 1
files = sorted(glob.glob("%{buildroot}%{_datadir}/themes/*/gtk-4.0/*.css"))
assert files, "no gtk-4.0 css found to validate"
for cur in files:
    prov = Gtk.CssProvider()
    prov.connect("parsing-error", on_err)
    prov.load_from_path(cur)
print("GTK4 CSS parse check: " + str(len(files)) + " file(s), " + str(real) + " real error(s)")
sys.exit(1 if real else 0)
PYEOF
# Shell node-gate: the GNOME 50 selectors must have compiled into gnome-shell.css
for css in %{buildroot}%{_datadir}/themes/*/gnome-shell/gnome-shell.css; do
  grep -q 'a11y-button' "$css" || { echo "node-gate FAIL: .a11y-button missing in $css"; exit 1; }
  grep -q 'message-list-clear-button' "$css" || { echo "node-gate FAIL: .message-list-clear-button missing in $css"; exit 1; }
done
echo "shell node-gate: OK"

%files
%{_datarootdir}/themes

%changelog
* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 20250817-5
- Patch0 (gnome50-selectors): style the GNOME 50 login .a11y-button and
  notification .message-list-clear-button using the theme's own existing
  styling (additive sibling selectors, inert on GNOME < 49)
- Patch1 (gnome50-appearance): import GNOME 50 native geometry
  (login-dialog-bottom-button-group 32px padding / 16px spacing,
  message-list-clear-button pill border-radius)
- Selector-correctness and SCSS engine-parse verified; pixel appearance
  not machine-verified
- Add a %%check: parse the compiled gtk-4.0 CSS with the real GTK 4 engine
  (GtkCssProvider) and assert the GNOME 50 selectors compiled into
  gnome-shell.css (new BuildRequires: gtk4, python3-gobject-base)

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250817-4
- Drop GTK2-era runtime deps (adwaita-gtk2-theme, gtk-murrine-engine,
  gtk2-engines): adwaita-gtk2-theme was removed from Fedora 44 repos,
  and the gtk-2.0/ payload only matters for legacy GTK2 apps

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250817-3
- Replace gnome-themes-extra dep with Fedora's adwaita-gtk2-theme

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250817-2
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add gnome-themes-extra runtime dependency

* Sat Dec 13 2025 Hector Diaz <hdiazc@live.com> - 20250817-1
- Bump version

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20240522-3
- Include light

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20240522-2
- Dark theme only

* Sat Nov 30 2024 Hector Diaz <hdiazc@live.com> - 20240522-1
- Bump version

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230227-2
- Set options

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20230227-1
- Bump version

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20211225-2
- add gnome-shell

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20211225-1
- Initial version of the package
