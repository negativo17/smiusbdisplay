%global debug_package %{nil}

%ifarch x86_64
%global bin_folder x64
%endif

%ifarch aarch64
%global bin_folder aarch64
%endif

Name:       smiusbdisplay
Version:    4.7.1.0
Release:    1%{?dist}
Summary:    Silicon Motion USB display driver for SM76x and SM77x adapters
License:    BSD-3-Clause
URL:        https://www.siliconmotion.com/downloads/SM770-drivers.html

Source0:    %{name}-%{version}.tar.xz
Source1:    %{name}-generate-tarball.sh

Source10:   99-%{name}.rules
Source11:   %{name}.service
Source12:   20-%{name}.conf
Source13:   %{name}.logrotate
Source14:   com.siliconmotion.%{name}.metainfo.xml
Source15:   com.siliconmotion.%{name}.png

# The aarch64 binary requires glibc 2.34 and GLIBCXX_3.4.30 (GCC 12)
%if 0%{?rhel} == 8 || 0%{?rhel} == 9
ExclusiveArch:  x86_64
%else
ExclusiveArch:  x86_64 aarch64
%endif

BuildRequires:  chrpath
BuildRequires:  libappstream-glib
BuildRequires:  systemd-rpm-macros

Requires:   evdi-kmod >= 1.14.16
Requires:   libevdi >= 1.14.16
Requires:   logrotate

%description
This adds support for HDMI/DisplayPort/VGA adapters built upon the Silicon
Motion SM76x and SM77x series of USB display controllers. This includes
numerous docking stations, USB monitors, and USB adapters.

%if 0%{?fedora} || 0%{?rhel} < 10
%package -n xorg-x11-%{name}
Summary:        X.org X11 Silicon Motion USB display driver configuration
Requires:       %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires:       xorg-x11-server-Xorg%{?_isa}
Supplements:    (%{name} and xorg-x11-server-Xorg)

%description -n xorg-x11-%{name}
The Silicon Motion USB display X.org X11 driver configuration.
%endif

%prep
%autosetup

chrpath -d %{bin_folder}/SMIUSBDisplayManager

%build
# Nothing to build.

%install
mkdir -p \
    %{buildroot}%{_libexecdir}/%{name}/ \
    %{buildroot}/opt \
    %{buildroot}%{_udevrulesdir}/ \
    %{buildroot}%{_unitdir}/ \
    %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/ \
    %{buildroot}%{_sysconfdir}/logrotate.d/ \
    %{buildroot}%{_localstatedir}/log/SMIUSBDisplay/

# Main binary and firmware
install -p -m 0755 %{bin_folder}/SMIUSBDisplayManager %{buildroot}%{_libexecdir}/%{name}/
install -p -m 0644 *.bin %{buildroot}%{_libexecdir}/%{name}/

# The firmware path is hardcoded in the binary
ln -sr %{buildroot}%{_libexecdir}/%{name} %{buildroot}/opt/siliconmotion

%ifarch x86_64
# Firmware log capture tool
mkdir -p %{buildroot}%{_bindir}
install -p -m 0755 x64/SMIFWLogCapture %{buildroot}%{_bindir}/
%endif

# udev rules
install -p -m 0644 %{SOURCE10} %{buildroot}%{_udevrulesdir}/

# systemd unit
install -p -m 0644 %{SOURCE11} %{buildroot}%{_unitdir}/

%if 0%{?fedora} || 0%{?rhel} < 10
# X.org configuration
install -p -m 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/
%endif

# logrotate
install -p -m 0644 %{SOURCE13} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# AppStream metadata
install -p -m 0644 -D %{SOURCE14} %{buildroot}%{_metainfodir}/com.siliconmotion.%{name}.metainfo.xml
install -p -m 0644 -D %{SOURCE15} %{buildroot}%{_datadir}/pixmaps/com.siliconmotion.%{name}.png

%check
appstream-util validate --nonet %{buildroot}%{_metainfodir}/com.siliconmotion.%{name}.metainfo.xml

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc release-notes.txt
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%ifarch x86_64
%{_bindir}/SMIFWLogCapture
%endif
%{_datadir}/pixmaps/com.siliconmotion.%{name}.png
%{_libexecdir}/%{name}
%{_metainfodir}/com.siliconmotion.%{name}.metainfo.xml
%{_udevrulesdir}/99-%{name}.rules
%{_unitdir}/%{name}.service
%dir %{_localstatedir}/log/SMIUSBDisplay/
/opt/siliconmotion

%if 0%{?fedora} || 0%{?rhel} < 10
%files -n xorg-x11-%{name}
%{_sysconfdir}/X11/xorg.conf.d/20-%{name}.conf
%endif

%changelog
* Fri Oct 09 2026 Simone Caronni <negativo17@gmail.com> - 4.7.1.0-1
- First build.
