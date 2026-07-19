Name:           colloid-gtk-theme
Version:        20250731
Release:        7%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Colloid-gtk-theme
%define dversion 2025-07-31
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz
Patch0:         gnome50-selectors.patch
Patch1:         gnome50-appearance.patch
Patch2:         fix-fsf-address.patch

BuildRequires:  gnome-shell
BuildRequires:  sassc
# %%check: validate the compiled GTK4 CSS with the real GTK engine
BuildRequires:  gtk4
BuildRequires:  python3-gobject-base

%description
Theme for GNOME/GTK based desktop environments.
This package ships the license only; install a color package for the theme.

# Upstream spells the blue accent "default"; packages are named for the color.
%package blue
Summary:        Colloid GTK theme, blue accent
%description blue
Blue accent, standard size. Ships light, dark and auto variants.

%package blue-compact
Summary:        Colloid GTK theme, blue accent, compact
%description blue-compact
Blue accent, compact size. Ships light, dark and auto variants.

%package red
Summary:        Colloid GTK theme, red accent
%description red
Red accent, standard size. Ships light, dark and auto variants.

%package red-compact
Summary:        Colloid GTK theme, red accent, compact
%description red-compact
Red accent, compact size. Ships light, dark and auto variants.

%package grey
Summary:        Colloid GTK theme, grey accent
%description grey
Grey accent, standard size. Ships light, dark and auto variants.

%package grey-compact
Summary:        Colloid GTK theme, grey accent, compact
%description grey-compact
Grey accent, compact size. Ships light, dark and auto variants.

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# -s takes one value per call and defaults to standard, so run it twice.
# -l omitted: verified no-op for the buildroot (note: -l fixed is NOT a no-op,
# but is not used here).
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  -t default -t red -t grey -s standard
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  -t default -t red -t grey -s compact
# -hdpi/-xhdpi contain only xfwm4 assets: no gtk-4.0, no gnome-shell, not even
# an index.theme. They are unusable on GNOME.
rm -rf %{buildroot}%{_datarootdir}/themes/*-hdpi
rm -rf %{buildroot}%{_datarootdir}/themes/*-xhdpi
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
# Unlike Fluent, install.sh here never drops a COPYING/LICENSE copy into theme
# dirs (verified: no COPYING/LICENSE reference in install.sh), so there is no
# in-tree duplicate to strip.

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
for d in cinnamon xfwm4 plank unity; do
  found=$(find %{buildroot}%{_datadir}/themes -maxdepth 2 -type d -name "$d" | wc -l)
  [ "$found" -eq 0 ] || { echo "strip FAIL: $found $d dirs remain"; exit 1; }
done
echo "strip gate: OK"
hdpi=$(find %{buildroot}%{_datadir}/themes -maxdepth 1 -type d \
  \( -name '*-hdpi' -o -name '*-xhdpi' \) | wc -l)
[ "$hdpi" -eq 0 ] || { echo "dpi gate FAIL: $hdpi hdpi dir(s) remain"; exit 1; }
echo "dpi gate: OK"

%files
%license LICENSE

%files blue
%license LICENSE
%{_datarootdir}/themes/Colloid
%{_datarootdir}/themes/Colloid-Light
%{_datarootdir}/themes/Colloid-Dark

%files blue-compact
%license LICENSE
%{_datarootdir}/themes/Colloid-Compact
%{_datarootdir}/themes/Colloid-Light-Compact
%{_datarootdir}/themes/Colloid-Dark-Compact

%files red
%license LICENSE
%{_datarootdir}/themes/Colloid-Red
%{_datarootdir}/themes/Colloid-Red-Light
%{_datarootdir}/themes/Colloid-Red-Dark

%files red-compact
%license LICENSE
%{_datarootdir}/themes/Colloid-Red-Compact
%{_datarootdir}/themes/Colloid-Red-Light-Compact
%{_datarootdir}/themes/Colloid-Red-Dark-Compact

%files grey
%license LICENSE
%{_datarootdir}/themes/Colloid-Grey
%{_datarootdir}/themes/Colloid-Grey-Light
%{_datarootdir}/themes/Colloid-Grey-Dark

%files grey-compact
%license LICENSE
%{_datarootdir}/themes/Colloid-Grey-Compact
%{_datarootdir}/themes/Colloid-Grey-Light-Compact
%{_datarootdir}/themes/Colloid-Grey-Dark-Compact

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250731-7
- Split into color/size packages (blue, red, grey x standard, compact). Blue is
  upstream's "default" accent; packages are named for the color.
- Drop -hdpi/-xhdpi: those directories hold only xfwm4 assets (no gtk-4.0, no
  gnome-shell, no index.theme) and are unusable on GNOME. Gated in %%check.
- Strip cinnamon/xfwm4/plank/unity; keep gtk-2.0 and metacity-1.
- Drop -l/--libadwaita: verified byte-identical buildroot without it.

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250731-6
- Own only the installed theme directories, not %%{_datarootdir}/themes itself:
  that directory belongs to the filesystem package, and co-owning it is the
  standard-dir-owned-by-package defect.

* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 20250731-5
- Patch0 (gnome50-selectors): style the GNOME 50 login .a11y-button and
  notification .message-list-clear-button using the theme's own existing
  styling (additive sibling selectors; inert on GNOME < 49)
- Patch1 (gnome50-appearance): import GNOME 50 native geometry
  (login-dialog-bottom-button-group 32px padding / 16px spacing,
  message-list-clear-button pill border-radius)
- Selector-correctness and SASS engine-parse verified; pixel appearance
  not machine-verified
- Patch2 (fix-fsf-address): update the outdated FSF postal address in the
  upstream gnome-shell.css GPL header to the canonical URL form, clearing
  rpmlint incorrect-fsf-address errors
- Add a %%check: parse the compiled gtk-4.0 CSS with the real GTK 4 engine
  (GtkCssProvider) and assert the GNOME 50 selectors compiled into
  gnome-shell.css (new BuildRequires: gtk4, python3-gobject-base)

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250731-4
- Drop GTK2-era runtime deps (adwaita-gtk2-theme, gtk-murrine-engine):
  adwaita-gtk2-theme was removed from Fedora 44 repos, and the gtk-2.0/
  payload only matters for legacy GTK2 apps

* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250731-3
- Replace gnome-themes-extra dep with Fedora's adwaita-gtk2-theme

* Sat May 02 2026 Hector Diaz <hdiazc@live.com> - 20250731-2
- Modernize: SPDX license tag (GPLv3+ → GPL-3.0-or-later)
- Add gnome-themes-extra runtime dependency

* Sat Dec 13 2025 Hector Diaz <hdiazc@live.com> - 20250731-1
- Bump version

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20241116-2
- Include light

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241116-1
- Initial version of the package
