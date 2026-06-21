Name:           orchis-theme
Version:        20250425
Release:        5%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Orchis-theme
%define dversion 2025-04-25
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz
Patch0:         gnome50-selectors.patch
Patch1:         gnome50-appearance.patch
Patch2:         fix-gtk4-define-color.patch

BuildRequires:  gnome-shell
BuildRequires:  sassc
# %%check: validate the compiled GTK4 CSS with the real GTK engine
BuildRequires:  gtk4
BuildRequires:  python3-gobject-base

%description
Orchis is a Material Design theme for GNOME/GTK based desktop environments.
Based on nana-4 -- materia-theme

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh --icon gnome -t grey -c dark --libadwaita --dest %{buildroot}%{_datarootdir}/themes

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
* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 20250425-5
- Patch0 (gnome50-selectors): style the GNOME 50 login .a11y-button and
  notification .message-list-clear-button using the theme's own existing
  styling (additive sibling selectors, inert on GNOME < 49)
- Patch1 (gnome50-appearance): import GNOME 50 native geometry
  (login-dialog-bottom-button-group 32px padding / 16px spacing,
  message-list-clear-button pill border-radius)
- Switch %%prep to %%autosetup -p1
- Add a %%check: parse the compiled gtk-4.0 CSS with the real GTK 4 engine
  (GtkCssProvider) and assert the GNOME 50 selectors compiled into
  gnome-shell.css (new BuildRequires: gtk4, python3-gobject-base)
- Selector-correctness and engine-parse verified; pixel appearance
  not machine-verified
- Patch2 (fix-gtk4-define-color): fix a pre-existing GTK 4 parse error the
  %%check surfaced. The libadwaita build emitted
  "@define-color theme_{,unfocused_}selected_bg_color var(--accent-bg-color)",
  which GTK's @define-color cannot parse ("Expected a valid color"). Use the
  defined @accent_color named color in the libadwaita case only (guarded by
  type-of($primary)), leaving the valid GTK3 literal untouched. Verified 0 GTK4
  parse errors via the real engine; present in upstream master too.

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250425-4
- Drop GTK2-era runtime deps (adwaita-gtk2-theme, gtk-murrine-engine):
  adwaita-gtk2-theme was removed from Fedora 44 repos, and the gtk-2.0/
  payload only matters for legacy GTK2 apps

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250425-3
- Replace gnome-themes-extra dep with Fedora's adwaita-gtk2-theme

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250425-2
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add gnome-themes-extra runtime dependency

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250425-1
- Bump version

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241103-1
- Initial version of the package
