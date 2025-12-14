Name:           colloid-gtk-theme
Version:        20250731
Release:        1%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPLv3+

%define dname Colloid-gtk-theme
%define dversion 2025-07-31
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

Requires:       gtk-murrine-engine

BuildRequires:  gnome-shell
BuildRequires:  sassc

%description
Theme for GNOME/GTK based desktop environments.

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh -t grey --libadwaita --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sat Dec 13 2025 Hector Diaz <hdiazc@live.com> - 20250731-1
- Bump version

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20241116-2
- Include light

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241116-1
- Initial version of the package