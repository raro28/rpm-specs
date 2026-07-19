Name:           fluent-gtk-theme-compact
Version:        20250417
Release:        8%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Fluent-gtk-theme
%define dversion 2025-04-17
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz
Patch0:         gnome50-selectors.patch
Patch1:         gnome50-appearance.patch
# St's shell CSS engine rejects the keyword value in the upstream
# #panelActivities "background-position: center center" (logged at runtime as
# "Ignoring length property that isn't a number"). St already falls back to 0 0,
# so the numeric form is pixel-identical and silences the warning.
Patch2:         fix-shell-bg-position.patch

BuildRequires:  gnome-shell
BuildRequires:  sassc
# %%check: validate the compiled GTK4 CSS with the real GTK engine
BuildRequires:  gtk4
BuildRequires:  python3-gobject-base

%description
Fluent is a Fluent design theme for GNOME/GTK based desktop environments

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh --dest %{buildroot}%{_datarootdir}/themes --theme grey -i gnome --size compact --tweaks solid round -l

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
%{_datarootdir}/themes/*

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250417-8
- Own only the installed theme directories, not %%{_datarootdir}/themes itself:
  that directory belongs to the filesystem package, and co-owning it is the
  standard-dir-owned-by-package defect.

* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 20250417-7
- Patch2 (fix-shell-bg-position): the upstream #panelActivities rule sets
  "background-position: center center", a keyword St's CSS engine cannot parse —
  it logs "Ignoring length property that isn't a number" on every theme load and
  drops the declaration, falling back to 0 0. Set the numeric 0 0 explicitly in
  the gnome-shell %%activities_icon placeholder. St already rendered at 0 0
  (background-size: auto), so this is no visual change; silences the runtime
  warning. Verified: the compiled gnome-shell.css no longer carries a keyword
  background-position.

* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 20250417-6
- Patch0 (gnome50-selectors): style the GNOME 50 login .a11y-button and the
  notification .message-list-clear-button with the theme's own button styling
  by adding them as sibling selectors (.a11y-button to the login
  .cancel-button group; .message-list-clear-button to the .dnd-button rule).
  Additive only, inert on GNOME < 49 where the selectors do not exist.
- Patch1 (gnome50-appearance): import GNOME 50's native geometry
  (.login-dialog-bottom-button-group padding 32px / spacing 16px;
  .message-list-clear-button pill border-radius 999px).
- Switch %%prep to %%autosetup -p1 to apply the patches.
- Appearance verified for selector-correctness and SCSS engine parse only,
  not for pixel-level rendering.
- Add a %%check: parse the compiled gtk-4.0 CSS with the real GTK 4 engine
  (GtkCssProvider) and assert the GNOME 50 selectors compiled into
  gnome-shell.css (new BuildRequires: gtk4, python3-gobject-base).

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250417-5
- Drop GTK2-era runtime deps (adwaita-gtk2-theme, gtk-murrine-engine):
  adwaita-gtk2-theme was removed from Fedora 44 repos, and the gtk-2.0/
  payload only matters for legacy GTK2 apps

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250417-4
- Replace gnome-themes-extra dep with Fedora's adwaita-gtk2-theme

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250417-3
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add -l (libadwaita) to install.sh for GTK4/libadwaita app theming

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250417-2
- Include light

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250417-1
- Bump version

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20240612-2
- Dark theme only

* Sat Nov 30 2024 Hector Diaz <hdiazc@live.com> - 20240612-1
- Bump version

* Mon Mar 06 2023 Hector Diaz <hdiazc@live.com> - 20221215-1
- Bump version

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220115-2
- add gnome-shell

* Sun Feb 27 2022 Hector Diaz <hdiazc@live.com> - 20220115-1
- Initial version of the package
