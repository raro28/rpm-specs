Name:           orchis-gtk-theme
Version:        20260707
Release:        3%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Orchis-theme
%define dversion 2026-07-07
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz#/%{dname}-%{dversion}.tar.gz
Patch0:         gnome50-selectors.patch
Patch1:         gnome50-appearance.patch
Patch2:         fix-gtk4-define-color.patch
# St's shell CSS engine rejects the keyword value in the upstream
# #panelActivities "background-position: center center" (logged at runtime as
# "Ignoring length property that isn't a number"). St already falls back to 0 0,
# so the numeric form is pixel-identical and silences the warning.
Patch3:         fix-shell-bg-position.patch

BuildRequires:  gnome-shell
BuildRequires:  sassc
# %%check: validate the compiled GTK4 CSS with the real GTK engine
BuildRequires:  gtk4
BuildRequires:  python3-gobject-base

%description
Orchis is a Material Design theme for GNOME/GTK based desktop environments.
Based on nana-4 -- materia-theme
This package ships the license only; install a color package for the theme.

# Upstream spells the blue accent "default"; packages are named for the color.
%package blue
Summary:        Orchis GTK theme, blue accent
%description blue
Blue accent, standard size. Ships light, dark and auto variants.

%package blue-compact
Summary:        Orchis GTK theme, blue accent, compact
%description blue-compact
Blue accent, compact size. Ships light, dark and auto variants.

%package red
Summary:        Orchis GTK theme, red accent
%description red
Red accent, standard size. Ships light, dark and auto variants.

%package red-compact
Summary:        Orchis GTK theme, red accent, compact
%description red-compact
Red accent, compact size. Ships light, dark and auto variants.

%package grey
Summary:        Orchis GTK theme, grey accent
%description grey
Grey accent, standard size. Ships light, dark and auto variants.

%package grey-compact
Summary:        Orchis GTK theme, grey accent, compact
%description grey-compact
Grey accent, compact size. Ships light, dark and auto variants.

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# One call emits both sizes. -l omitted: verified no-op for the buildroot.
./install.sh --dest %{buildroot}%{_datarootdir}/themes \
  --icon gnome -t default -t red -t grey
rm -rf %{buildroot}%{_datarootdir}/themes/*-hdpi
rm -rf %{buildroot}%{_datarootdir}/themes/*-xhdpi
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
find %{buildroot}%{_datarootdir}/themes -name COPYING -delete

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
%license COPYING

%files blue
%license COPYING
%{_datarootdir}/themes/Orchis
%{_datarootdir}/themes/Orchis-Light
%{_datarootdir}/themes/Orchis-Dark

%files blue-compact
%license COPYING
%{_datarootdir}/themes/Orchis-Compact
%{_datarootdir}/themes/Orchis-Light-Compact
%{_datarootdir}/themes/Orchis-Dark-Compact

%files red
%license COPYING
%{_datarootdir}/themes/Orchis-Red
%{_datarootdir}/themes/Orchis-Red-Light
%{_datarootdir}/themes/Orchis-Red-Dark

%files red-compact
%license COPYING
%{_datarootdir}/themes/Orchis-Red-Compact
%{_datarootdir}/themes/Orchis-Red-Light-Compact
%{_datarootdir}/themes/Orchis-Red-Dark-Compact

%files grey
%license COPYING
%{_datarootdir}/themes/Orchis-Grey
%{_datarootdir}/themes/Orchis-Grey-Light
%{_datarootdir}/themes/Orchis-Grey-Dark

%files grey-compact
%license COPYING
%{_datarootdir}/themes/Orchis-Grey-Compact
%{_datarootdir}/themes/Orchis-Grey-Light-Compact
%{_datarootdir}/themes/Orchis-Grey-Dark-Compact

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-3
- Rename to orchis-gtk-theme: -gtk-theme is the Fedora plurality for GTK themes
  and makes this repo internally consistent. Clean break, no Obsoletes/Provides.
- Split into color/size packages (blue, red, grey x standard, compact).
- Drop -hdpi/-xhdpi (xfwm4-only, unusable on GNOME); gated in %%check.
- Strip cinnamon/xfwm4/plank/unity; keep gtk-2.0 and metacity-1.
- Drop -l/--libadwaita: verified byte-identical buildroot without it.

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-2
- Own only the installed theme directories, not %%{_datarootdir}/themes itself:
  that directory belongs to the filesystem package, and co-owning it is the
  standard-dir-owned-by-package defect.

* Sat Jul 11 2026 Hector Diaz <hdiazc@live.com> - 20260707-1
- Bump to upstream 2026-07-07. All four downstream patches still apply and remain
  necessary against the new source: upstream still tops out at widgets-48-0 (no
  native GNOME 49/50 sheet), still lacks .a11y-button / the
  .login-dialog-bottom-button-group / the .message-list-clear-button coverage
  (Patch0/Patch1), and still carries the GTK4 @define-color var() parse bug
  (Patch2) and the keyword #panelActivities background-position (Patch3).
  install.sh flags unchanged (-t grey -c dark -i gnome --libadwaita). Patches
  apply with line-offset only; %%check (GTK4 CSS engine parse + shell node-gate)
  passes.
- Source0: add a #/%%{dname}-%%{dversion}.tar.gz download rename. The bare
  archive name collided with whitesur-icon-theme (both now carry the 2026-07-07
  tag), so a shared ~/rpmbuild/SOURCES/ served the wrong tarball to %%prep.

* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 20250425-6
- Patch3 (fix-shell-bg-position): the upstream #panelActivities rule sets
  "background-position: center center", a keyword St's CSS engine cannot parse —
  it logs "Ignoring length property that isn't a number" on every theme load and
  drops the declaration, falling back to 0 0. Set the numeric 0 0 explicitly in
  the gnome-shell %%icon_activities placeholder. Pixel-identical (icon size equals
  the 24px box, and St already rendered at 0 0); silences the runtime warning.
  Verified: the compiled gnome-shell.css no longer carries a keyword
  background-position.

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
