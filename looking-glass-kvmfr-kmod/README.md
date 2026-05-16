# looking-glass-kvmfr-kmod

Fedora `akmod` packaging of the `kvmfr` ("KVM Frame Relay") kernel module
extracted from upstream [LookingGlass](https://github.com/gnif/LookingGlass)
tag `B7`. Replaces the legacy `/dev/shm/looking-glass` IVSHMEM file backing
with a DMA-BUF–capable character device (`/dev/kvmfr0`) for zero-copy GPU
frame transfer between a VFIO host and a Windows passthrough guest.

## Packages produced

| Package | Arch | What it ships |
|---|---|---|
| `akmod-kvmfr` | x86_64 | Source SRPM + akmods scaffolding (per-kernel rebuild on host) |
| `kmod-kvmfr` | x86_64 | Empty meta-package; pulls latest per-kernel kmod |
| `kvmfr-kmod-common` | noarch | `/usr/lib/modprobe.d/kvmfr.conf`, `/usr/lib/udev/rules.d/99-kvmfr.rules`, `/usr/lib/modules-load.d/kvmfr.conf`, LICENSE |
| `kvmfr-kmod-selinux` | noarch | Targeted SELinux policy `kvmfr.pp` defining `kvmfr_device_t` and granting `svirt_t` access |

The `.ko` itself is **not built in COPR**. `akmod-kvmfr` ships source; the
`akmods` service rebuilds it on your machine against your installed kernel
and re-runs automatically after every `dnf update kernel`.

## What's automated for you

On `dnf install` / upgrade:

- **`akmods` triggers a per-kernel rebuild** producing `kmod-kvmfr-<kver>` and installing the `.ko` at `/lib/modules/<kver>/extra/kvmfr/kvmfr.ko.xz`
- **`modprobe kvmfr` runs at every boot** (via `systemd-modules-load.service` reading `/usr/lib/modules-load.d/kvmfr.conf`) — `/dev/kvmfr0` exists before libvirt VMs try to start
- **`/dev/kvmfr0` is owned by `<user>:kvm` mode 0660** (via the udev rule shipped in `kvmfr-kmod-common`; default user is `ekthor` — edit `99-kvmfr.rules` if your username differs)
- **Static memory size = 256 MiB** (`options kvmfr static_size_mb=256` in modprobe.d) — enough for any guest resolution up to 4K
- **SELinux policy module loaded + `/dev/kvmfr0` relabelled** to `kvmfr_device_t` so libvirt-managed VMs (running as `svirt_t`) can open it

After first install, `lsmod | grep kvmfr` should show the module, and `ls -lZ /dev/kvmfr0` should show:
```
crw-rw----. 1 <user> kvm system_u:object_r:kvmfr_device_t:s0  /dev/kvmfr0
```

## Manual host configuration this package cannot do for you

Two host-side changes you must make yourself, both **persistent** across
reboots once applied:

### 1. Add `/dev/kvmfr0` to libvirt's `cgroup_device_acl`

libvirt's per-VM cgroup denies qemu access to any device not on its
whitelist. The default list does **not** include `/dev/kvmfr0`, so qemu
gets `Permission denied` even though file-level DAC + SELinux allow it.

Append to `/etc/libvirt/qemu.conf`:

```ini
cgroup_device_acl = [
    "/dev/null", "/dev/full", "/dev/zero",
    "/dev/random", "/dev/urandom",
    "/dev/ptmx", "/dev/userfaultfd",
    "/dev/kvm",
    "/dev/kvmfr0"
]
```

Then restart the libvirt daemon:

```bash
sudo systemctl restart virtqemud
```

(On older libvirt: `sudo systemctl restart libvirtd`.)

### 2. Switch the VM's IVSHMEM backing from `/dev/shm` to `/dev/kvmfr0`

This is a per-VM XML edit. Shut the VM down first, then:

```bash
sudo virsh dumpxml win11-system > /tmp/win11.xml
# Back up first:
cp /tmp/win11.xml ~/win11-pre-kvmfr.xml.bak
# Edit /tmp/win11.xml:
#   * Add xmlns:qemu to the <domain> element
#   * Remove any existing <shmem name='looking-glass'>...</shmem> block
#   * Add a <qemu:commandline> block as below
sudo virsh define /tmp/win11.xml
```

Diff:

```diff
-<domain type='kvm'>
+<domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
   ...
-    <shmem name='looking-glass'>
-      <model type='ivshmem-plain'/>
-      <size unit='M'>256</size>
-      <address type='pci' domain='0x0000' bus='0x10' slot='0x01' function='0x0'/>
-    </shmem>
   </devices>
+  <qemu:commandline>
+    <qemu:arg value='-device'/>
+    <qemu:arg value="{'driver':'ivshmem-plain','id':'shmem0','memdev':'looking-glass'}"/>
+    <qemu:arg value='-object'/>
+    <qemu:arg value="{'qom-type':'memory-backend-file','id':'looking-glass','mem-path':'/dev/kvmfr0','size':268435456,'share':true}"/>
+  </qemu:commandline>
 </domain>
```

The `size` value is bytes: `256 * 1024 * 1024 = 268435456`. It **must
match** `static_size_mb` in the modprobe.d config.

### 3. (optional) Customize user / size

- If your host login user isn't `ekthor`, edit `OWNER=` in `/usr/lib/udev/rules.d/99-kvmfr.rules` (or drop a higher-priority rule in `/etc/udev/rules.d/`)
- For non-256-MiB sizes, change **both** `/usr/lib/modprobe.d/kvmfr.conf` (`static_size_mb=N`) **and** the `size` in the VM XML (`N * 1024 * 1024`)
- Sizing formula per upstream docs: `width × height × 4 × 2 + 10 MiB`. 32 MiB is enough for 1080p, 64 for 1440p, 128 for 4K.

## Guest-side (Windows)

**No changes needed in the guest when switching from `/dev/shm` to `/dev/kvmfr0`.**

The IVSHMEM PCI device looks identical to the guest regardless of how the
host backs it. The bundled `looking-glass-host` Windows service (installed
via `looking-glass-host-setup.exe` from <https://looking-glass.io/downloads>)
re-binds to the device automatically after the VM restarts. The host
service version must match the client's B-series (currently `B7`).

## Verifying end-to-end

After starting the VM:

```bash
# Refcount > 0 means qemu has /dev/kvmfr0 mapped
lsmod | grep kvmfr
# No AVC denials should appear:
sudo ausearch -m AVC -ts recent | grep kvmfr || echo "no denials"
# libvirt didn't error out:
sudo journalctl -u virtqemud --since '1 minute ago' | grep -iE 'kvmfr|error'
```

Inside Windows, the IVSHMEM device should appear under **Device Manager →
System devices** with the Looking Glass driver loaded. Then launch
`looking-glass-client` with `-f /dev/kvmfr0` (the `looking-glass-client`
RPM ships dedicated `Kvmfr` and `Fullscreen + kvmfr` desktop actions for
GNOME search).

## Rollback

To go back to `/dev/shm/looking-glass`:

```bash
sudo virsh destroy win11-system     # stop the running VM
sudo virsh define ~/win11-pre-kvmfr.xml.bak
sudo virsh start win11-system
```

The kvmfr module + config can stay loaded — it does no harm when unused.
To fully uninstall:

```bash
sudo dnf remove akmod-kvmfr kmod-kvmfr kvmfr-kmod-common kvmfr-kmod-selinux
sudo modprobe -r kvmfr
```

This also removes the SELinux module via the `%postun` scriptlet.

## Layout reference

```
/usr/lib/modprobe.d/kvmfr.conf                  # static_size_mb=256
/usr/lib/udev/rules.d/99-kvmfr.rules            # owner/group/mode for /dev/kvmfr0
/usr/lib/modules-load.d/kvmfr.conf              # boot-time autoload
/usr/share/selinux/packages/kvmfr.pp            # SELinux policy module
/lib/modules/<kver>/extra/kvmfr/kvmfr.ko.xz     # the kernel module (built by akmods)
/usr/src/akmods/looking-glass-kvmfr-kmod-*.src.rpm  # source for akmods rebuilds
```

## Source files in this directory

| File | Role |
|---|---|
| `looking-glass-kvmfr-kmod.spec` | The spec |
| `kvmfr.conf` | Modprobe options (`Source1`) |
| `99-kvmfr.rules` | Udev rule (`Source2`) |
| `kvmfr.te` | SELinux type enforcement (`Source3`) |
| `kvmfr.fc` | SELinux file contexts (`Source4`) |
| `kvmfr-modules-load.conf` | systemd-modules-load.d snippet (`Source5`) |
| `0001-add-module-description.patch` | One-line patch silencing modpost warning |

`Source0` is the upstream `LookingGlass-B7.tar.gz` fetched from
`github.com/gnif/LookingGlass`.
