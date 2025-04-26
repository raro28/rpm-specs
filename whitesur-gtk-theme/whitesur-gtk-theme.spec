Name:           whitesur-gtk-theme
Version:        20250403
Release:        2%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPLv3+

%define dname WhiteSur-gtk-theme
%define dversion 2025-04-03
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz

BuildRequires: glib2-devel
BuildRequires:  sassc
BuildRequires:  sudo
BuildRequires:  dialog

%description
A macOS like theme for Linux GTK Desktops

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/themes
./install.sh -t grey -N mojave -l --shell -i gnome --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250403-2
- Include light

* Sat Apr 26 2025 Hector Diaz <hdiazc@live.com> - 20250403-1
- Bump version

* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241118-1
- Initial release