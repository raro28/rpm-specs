%global srcname astra-monitor
%global uuid    monitor@astraext.github.io

Name:           gnome-shell-extension-astra-monitor
Version:        42
Release:        1%{?dist}
Summary:        GNOME Shell extension monitoring CPU, GPU, memory, disk, network and sensors
BuildArch:      noarch

License:        GPL-3.0-or-later
URL:            https://github.com/AstraExt/%{srcname}
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz
# Upstream's CI-built release artifact. Never installed: %%check diffs the
# JavaScript this spec compiles against it, so a divergent tsc emit fails the build.
Source1:        %{url}/releases/download/v%{version}/%{uuid}.shell-extension.zip

# Authored in TypeScript; compiled here with Fedora's tsc.
BuildRequires:  typescript
# glib-compile-schemas
BuildRequires:  glib2-devel
# msgfmt
BuildRequires:  gettext
# unpacks Source1 for %%check
BuildRequires:  unzip

# metadata.json declares shell-version 45-51.
Requires:       (gnome-shell >= 45 with gnome-shell < 52)

# Optional data sources, each gating one feature; the extension runs without them.
# libgtop2: GTop CPU/process data source, the alternative to /proc parsing.
Recommends:     libgtop2
# lm_sensors: the `sensors` command, the only temperature/fan/voltage source.
Recommends:     lm_sensors
# nethogs: per-process network I/O; needs root or cap_net_admin+cap_net_raw.
Recommends:     nethogs

%description
Astra Monitor is a system monitor for the GNOME Shell top bar. It reports CPU,
GPU, memory, disk, network and sensor readings, each with a configurable header
widget and a drop-down with per-device detail and top processes.

Installed system-wide. Enable it per user with:
    gnome-extensions enable %{uuid}

%prep
%autosetup -n %{srcname}-%{version}

%build
glib-compile-schemas schemas/

# tsc exits non-zero here: the @girs/* ambient type packages are npm-only and
# absent from the build root, so every gi:// and resource:// import is reported
# unresolved. Emission is unaffected -- %%check proves the result is byte-identical
# to upstream's CI build.
tsc || :

for po in po/*.po; do
    lang=$(basename "$po" .po)
    install -d locale/"$lang"/LC_MESSAGES
    msgfmt -o locale/"$lang"/LC_MESSAGES/%{uuid}.mo "$po"
done

%check
# Ground truth: upstream's release artifact for this exact tag.
mkdir -p _upstream
unzip -q %{SOURCE1} -d _upstream

# The set of compiled files must match, and every one must be byte-identical.
(cd build && find . -name '*.js' | sort) > _built.list
(cd _upstream && find . -name '*.js' | sort) > _released.list
diff -u _built.list _released.list

while read -r f; do
    cmp "build/$f" "_upstream/$f"
done < _built.list

# The compiled catalogs must match too.
(cd locale && find . -name '*.mo' | sort) > _built-mo.list
(cd _upstream/locale && find . -name '*.mo' | sort) > _released-mo.list
diff -u _built-mo.list _released-mo.list

while read -r f; do
    cmp "locale/$f" "_upstream/locale/$f"
done < _built-mo.list

# The shell this package targets must stay inside the declared range.
grep -q '"50"' metadata.json

%install
extdir=%{buildroot}%{_datadir}/gnome-shell/extensions/%{uuid}
install -d "$extdir"

cp -a build/extension.js build/prefs.js build/src "$extdir"/
cp -a icons schemas "$extdir"/
install -pm 0644 metadata.json stylesheet.css "$extdir"/

find "$extdir" -type d -exec chmod 0755 {} +
find "$extdir" -type f -exec chmod 0644 {} +

# Catalogs go to the system locale tree, not the extension's own locale/ dir:
# the shell binds the gettext domain there for extensions installed in its own
# prefix. This is what Fedora's dash-to-panel, appindicator and just-perfection
# packages do, and it is what lets %%find_lang mark the files %%lang.
install -d %{buildroot}%{_datadir}/locale
cp -a locale/* %{buildroot}%{_datadir}/locale/
find %{buildroot}%{_datadir}/locale -type f -exec chmod 0644 {} +

%find_lang %{uuid}

%files -f %{uuid}.lang
%license LICENSE
%doc README.md
%{_datadir}/gnome-shell/extensions/%{uuid}/

%changelog
* Sat Sep 05 2026 Hector Diaz <hdiazc@live.com> - 42-1
- Initial package
