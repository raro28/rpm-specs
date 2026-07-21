# Upstream tag 2026-07-07 supersedes the previously-pinned master snapshot
# (commit a83f467, 2026-05-25) — it is 12 commits newer and carries the same
# "Fixed gnome 50 issues" work (the $GNOME_SHELL version-gating mechanism +
# quick-settings fix) that originally forced the commit pin. It still tops out
# at the widgets-48-0 shell stylesheet (no native GNOME 49/50 sheet), so the
# downstream GNOME 50 login / notification patches below remain necessary.
Name:           whitesur-gtk-theme
Version:        20260707
Release:        3%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname WhiteSur-gtk-theme
%define dversion 2026-07-07
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz#/%{dname}-%{dversion}.tar.gz
# Downstream GNOME 50 styling, split into the uniform two-patch model shared with
# the other vinceliuice themes. Patch0 (selectors) carries theme-native node
# coverage: .a11y-button gains WhiteSur's login system-button look, and the
# notification .message-list-clear-button is styled alongside .dnd-button. Patch1
# (appearance) carries GNOME-native geometry: the .login-dialog-bottom-button-group
# 32px/16px spacing and the .message-list-clear-button pill radius. Additive only —
# these selectors don't exist pre-50, so the rules are inert on older shells.
Patch0:         gnome50-selectors.patch
Patch1:         gnome50-appearance.patch
Patch2:         fix-fsf-address.patch
# St's shell CSS engine rejects the keyword value in the upstream
# #panelActivities "background-position: center center" (logged at runtime as
# "Ignoring length property that isn't a number"). St already falls back to 0 0,
# so the numeric form is pixel-identical and silences the warning.
Patch3:         fix-shell-bg-position.patch

BuildRequires:  glib2-devel
BuildRequires:  gnome-shell
BuildRequires:  sassc
BuildRequires:  sudo
# %%check: validate the compiled GTK4 CSS with the real GTK engine
BuildRequires:  gtk4
BuildRequires:  python3-gobject-base

%description
A macOS like theme for Linux GTK Desktops
This package ships the license only; install a color package for the theme.

%package blue
Summary:        WhiteSur GTK theme, blue accent
%description blue
Blue accent, translucent panel. Ships light and dark variants.

%package blue-solid
Summary:        WhiteSur GTK theme, blue accent, opaque
%description blue-solid
Blue accent, opaque panel. Ships light and dark variants.

%package red
Summary:        WhiteSur GTK theme, red accent
%description red
Red accent, translucent panel. Ships light and dark variants.

%package red-solid
Summary:        WhiteSur GTK theme, red accent, opaque
%description red-solid
Red accent, opaque panel. Ships light and dark variants.

%package grey
Summary:        WhiteSur GTK theme, grey accent
%description grey
Grey accent, translucent panel. Ships light and dark variants.

%package grey-solid
Summary:        WhiteSur GTK theme, grey accent, opaque
%description grey-solid
Grey accent, opaque panel. Ships light and dark variants.

%prep
%autosetup -p1 -n %{dname}-%{dversion}

%build
# Prebuilt assets; nothing to compile (install.sh handles SASS).

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
# WhiteSur spells blue explicitly. -l omitted: verified no-op for the buildroot,
# including alongside --shell.
./install.sh -d %{buildroot}%{_datarootdir}/themes \
  -t blue -t red -t grey -N mojave --shell -i gnome
rm -rf %{buildroot}%{_datarootdir}/themes/*-hdpi
rm -rf %{buildroot}%{_datarootdir}/themes/*-xhdpi
find %{buildroot}%{_datarootdir}/themes -maxdepth 2 -type d \
  \( -name cinnamon -o -name xfwm4 -o -name plank -o -name unity \) \
  -exec rm -rf {} +
# Unlike Fluent, install.sh here never drops a COPYING/LICENSE copy into theme
# dirs (verified: no COPYING reference anywhere in the source tree), so there
# is no in-tree duplicate to strip.

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
%{_datarootdir}/themes/WhiteSur-Light-blue
%{_datarootdir}/themes/WhiteSur-Dark-blue

%files blue-solid
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-solid-blue
%{_datarootdir}/themes/WhiteSur-Dark-solid-blue

%files red
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-red
%{_datarootdir}/themes/WhiteSur-Dark-red

%files red-solid
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-solid-red
%{_datarootdir}/themes/WhiteSur-Dark-solid-red

%files grey
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-grey
%{_datarootdir}/themes/WhiteSur-Dark-grey

%files grey-solid
%license COPYING
%{_datarootdir}/themes/WhiteSur-Light-solid-grey
%{_datarootdir}/themes/WhiteSur-Dark-solid-grey

%changelog
* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-3
- Split into color/opacity packages (blue, red, grey x normal, solid). WhiteSur
  has no size axis; its second axis is panel opacity.
- Drop -hdpi/-xhdpi (xfwm4-only, unusable on GNOME); gated in %%check.
- Strip cinnamon/xfwm4/plank/unity; keep gtk-2.0 and metacity-1.
- Drop -l/--libadwaita: verified byte-identical buildroot without it, including
  alongside --shell.

* Sun Jul 19 2026 Hector Diaz <hdiazc@live.com> - 20260707-2
- Own only the installed theme directories, not %%{_datarootdir}/themes itself:
  that directory belongs to the filesystem package, and co-owning it is the
  standard-dir-owned-by-package defect.

* Sat Jul 11 2026 Hector Diaz <hdiazc@live.com> - 20260707-1
- Switch from the pinned master commit (a83f467, 2026-05-25) to upstream tag
  2026-07-07 (12 commits newer; carries the same $GNOME_SHELL version-gating and
  quick-settings fixes that forced the pin). Drop the %%commit/%%shortcommit
  machinery and the date-versioning rationale; Source0 is now the tag archive
  with a #/%%{dname}-%%{dversion}.tar.gz download rename.
- All four downstream patches re-verified against the new source and kept: the
  release still tops out at widgets-48-0 (no native GNOME 49/50 sheet) and still
  lacks .a11y-button / .login-dialog-bottom-button-group / the widgets-48-0
  .message-list-clear-button coverage (Patch0/Patch1); the FSF postal address in
  gnome-shell _common.scss is still the old form (Patch2); %%apple_activites
  still uses the keyword background-position (Patch3). install.sh flags unchanged
  (-t grey -N mojave -l --shell -i gnome; mojave/gnome still valid variants).
  Patches apply with line-offset only; %%check passes.

* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 20260606-3
- Patch3 (fix-shell-bg-position): the upstream #panelActivities rule sets
  "background-position: center center", a keyword St's CSS engine cannot parse —
  it logs "Ignoring length property that isn't a number" on every theme load and
  drops the declaration, falling back to 0 0. Set the numeric 0 0 explicitly in
  the gnome-shell %%apple_activites placeholder. Pixel-identical (icon size equals
  the 24px box, and St already rendered at 0 0); silences the runtime warning.
  Verified: the compiled gnome-shell.css no longer carries a keyword
  background-position and the journal warning is gone after install.

* Sun Jun 21 2026 Hector Diaz <hdiazc@live.com> - 20260606-2
- Split the single GNOME 50 login patch into the uniform two-patch model now
  shared with the other vinceliuice themes (fluent/colloid/qogir):
  gnome50-selectors.patch (theme-native node coverage: the .a11y-button login
  buttons plus the newly-added notification .message-list-clear-button styled
  alongside .dnd-button) and gnome50-appearance.patch (GNOME 50 native geometry:
  the .login-dialog-bottom-button-group 32px/16px spacing and the
  .message-list-clear-button pill border-radius: 999px).
- Adds the notification clear-button coverage WhiteSur previously lacked.
- Additive/inert on GNOME < 49 (these selectors don't exist there).
  Selector-correctness and SASS engine-parse verified; pixel appearance on a
  live GNOME 50 session not machine-verified.
- Patch2 (fix-fsf-address): update the outdated FSF postal address in the
  upstream gnome-shell.css GPL header to the canonical URL form, clearing
  rpmlint incorrect-fsf-address errors.
- Add a %%check: parse the compiled gtk-4.0 CSS with the real GTK 4 engine
  (GtkCssProvider) and assert the GNOME 50 selectors compiled into
  gnome-shell.css (new BuildRequires: gtk4, python3-gobject-base).

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
