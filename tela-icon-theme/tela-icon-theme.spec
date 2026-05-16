Name:           tela-icon-theme
Version:        20250210
Release:        1%{?dist}
Summary:        A flat colorful Design icon theme
BuildArch:      noarch

License:        GPL-3.0-or-later

%define dname Tela-icon-theme
%define dversion 2025-02-10
URL:            https://github.com/vinceliuice/%{dname}
Source0:        https://github.com/vinceliuice/%{dname}/archive/refs/tags/%{dversion}.tar.gz#/%{dname}-%{dversion}.tar.gz

BuildRequires:  gtk-update-icon-cache

%description
A flat colorful Design icon theme.

%prep
%setup -n %{dname}-%{dversion}

%install
mkdir -p %{buildroot}%{_datarootdir}/icons
./install.sh -d "%{buildroot}%{_datarootdir}/icons" standard

%files
%{_datarootdir}/icons

%changelog
* Sat May 16 2026 Hector Diaz <hdiazc@live.com> - 20250210-1
- Initial version of the package
