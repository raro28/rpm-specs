Name:           fluent-gtk-theme
Version:        20250417
Release:        9%{?dist}
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
Fluent is a Fluent design theme for GNOME/GTK based desktop environments.
This package ships the license only; install a colour package for the theme.

# Upstream spells the blue accent "default"; packages are named for the colour.
%package blue
Summary:        Fluent GTK theme, blue accent
%description blue
Blue accent, standard size. Ships light, dark and auto variants.

%package blue-compact
Summary:        Fluent GTK theme, blue accent, compact
%description blue-compact
Blue accent, compact size. Ships light, dark and auto variants.

%package red
Summary:        Fluent GTK theme, red accent
%description red
Red accent, standard size. Ships light, dark and auto variants.

%package red-compact
Summary:        Fluent GTK theme, red accent, compact
%description red-compact
Red accent, compact size. Ships light, dark and auto variants.

%package grey
Summary:        Fluent GTK theme, grey accent
%description grey
Grey accent, standard size. Ships light, dark and auto variants.

%package grey-compact
Summary:        Fluent GTK theme, grey accent, compact
%description grey-compact
Grey accent, compact size. Ships light, dark and auto variants.

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# -s defaults to all sizes. -l omitted: it writes only to $HOME and adds no
# files to the buildroot.
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  -t default -t red -t grey -i gnome --tweaks solid round
# Desktops this COPR does not target. gtk-2.0 and metacity-1 are kept: 246 GTK2
# apps remain in F44, and gnome-flashback/metacity are installable GNOME
# sessions.
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
# install.sh drops a COPYING into every theme dir; %%license ships one copy per
# package under %%{_licensedir}, so the in-tree duplicates are redundant.
find %{buildroot}%{_datarootdir}/themes -name COPYING -delete

%check
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

%files
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/themes/Fluent-round
%{_datarootdir}/themes/Fluent-round-Light
%{_datarootdir}/themes/Fluent-round-Dark

%files blue-compact
%license COPYING
%{_datarootdir}/themes/Fluent-round-compact
%{_datarootdir}/themes/Fluent-round-Light-compact
%{_datarootdir}/themes/Fluent-round-Dark-compact

%files red
%license COPYING
%{_datarootdir}/themes/Fluent-round-red
%{_datarootdir}/themes/Fluent-round-red-Light
%{_datarootdir}/themes/Fluent-round-red-Dark

%files red-compact
%license COPYING
%{_datarootdir}/themes/Fluent-round-red-compact
%{_datarootdir}/themes/Fluent-round-red-Light-compact
%{_datarootdir}/themes/Fluent-round-red-Dark-compact

%files grey
%license COPYING
%{_datarootdir}/themes/Fluent-round-grey
%{_datarootdir}/themes/Fluent-round-grey-Light
%{_datarootdir}/themes/Fluent-round-grey-Dark

%files grey-compact
%license COPYING
%{_datarootdir}/themes/Fluent-round-grey-compact
%{_datarootdir}/themes/Fluent-round-grey-Light-compact
%{_datarootdir}/themes/Fluent-round-grey-Dark-compact

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20250417-9
- Rename from fluent-gtk-theme-compact: "compact" is a size variant, not a
  source package. Fedora expresses variants as subpackages
  (numix-icon-theme-circle, papirus-icon-theme-dark), never as separate source
  packages. Clean break, no Obsoletes/Provides.
- Split into colour/size packages (blue, red, grey x standard, compact). Blue is
  upstream's "default" accent; the package is named for the colour.
- Drop -l/--libadwaita. Verified byte-identical buildroots with and without it:
  it only writes $HOME/.config/gtk-4.0 and adds no files to the RPM. The
  20250417-3 changelog claim that it enabled GTK4/libadwaita theming was wrong
  in packaging terms.
- Strip cinnamon/xfwm4/plank/unity: this COPR targets GNOME only. gtk-2.0 and
  metacity-1 are kept deliberately.
- Extend %%check with a strip gate.
