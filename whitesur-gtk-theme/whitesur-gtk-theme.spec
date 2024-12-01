Name:           whitesur-gtk-theme
Version:        20241118
Release:        1%{?dist}
Summary:        Theme for GNOME/GTK based desktop environments
BuildArch:      noarch

License:        GPLv3+

%define dname WhiteSur-gtk-theme
%define dversion 2024-11-18
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dname}-%{dversion}.tar.gz

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
./install.sh -o solid -t grey -N mojave -l -c dark --shell -i gnome --dest %{buildroot}%{_datarootdir}/themes

%files
%{_datarootdir}/themes

%changelog
* Sun Dec 01 2024 Hector Diaz <hdiazc@live.com> - 20241118-1
- Initial release