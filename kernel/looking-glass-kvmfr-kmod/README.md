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
- **`/dev/kvmfr0` is owned by `<user>:kvm` mode 0660** (via the udev rule shipped in `kvmfr-kmod-common`; default user is `ekthor` — see [Customize user / size](#3-optional-customize-user--size) if yours differs)
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

This is a per-VM XML edit. Shut the VM down first, then save the current `/dev/shm` XML as a named backup (you'll want this for rollback) and produce the kvmfr variant:

```bash
sudo virsh dumpxml win11-system > ~/win11-system-shmem.xml   # rollback target
cp ~/win11-system-shmem.xml /tmp/win11-system-kvmfr.xml
# Edit /tmp/win11-system-kvmfr.xml:
#   * Add xmlns:qemu to the <domain> element
#   * Remove any existing <shmem name='looking-glass'>...</shmem> block
#   * Add a <qemu:commandline> block as below
sudo virsh define /tmp/win11-system-kvmfr.xml
sudo virsh dumpxml win11-system > ~/win11-system-kvmfr.xml   # save the canonical kvmfr form
```

The two `~/win11-system-{shmem,kvmfr}.xml` files become your one-command swap configs — see [Temporary swap](#temporary-swap-xml-only).

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

- **Different host user**: don't edit the shipped file — `/usr/lib/udev/rules.d/99-kvmfr.rules` is package-owned and gets reverted on upgrade. Instead drop a higher-priority rule in `/etc/udev/rules.d/`:
  ```
  # /etc/udev/rules.d/99-kvmfr.rules
  SUBSYSTEM=="kvmfr", OWNER="<your-user>", GROUP="kvm", MODE="0660"
  ```
  Then `sudo udevadm control --reload-rules && sudo udevadm trigger --subsystem-match=kvmfr`.
- **Non-256-MiB sizes**: change **both** the modprobe option (drop-in at `/etc/modprobe.d/kvmfr.conf` to override the shipped one) **and** the `size` in the VM XML (`N * 1024 * 1024` bytes). They must match.
- **Sizing formula** (per upstream docs): `width × height × 4 × 2 + 10 MiB`. 32 MiB covers 1080p, 64 for 1440p, 128 for 4K.

## Guest-side (Windows)

**No changes needed in the guest when switching from `/dev/shm` to `/dev/kvmfr0`.**

The IVSHMEM PCI device looks identical to the guest regardless of how the
host backs it. The bundled `looking-glass-host` Windows service (installed
via `looking-glass-host-setup.exe` from <https://looking-glass.io/downloads>)
re-binds to the device automatically after the VM restarts. The host
service version must match the client's B-series (currently `B7`).

## Verifying end-to-end

After `virsh start win11-system`, host-side:

```bash
# Refcount > 0 means something has it open (qemu, and later the client)
lsmod | grep kvmfr

# Who actually has /dev/kvmfr0 open — most authoritative check.
# Expect qemu at minimum; looking-glass-client appears once you launch it.
sudo lsof /dev/kvmfr0

# No SELinux denials related to kvmfr:
sudo ausearch -m AVC -ts recent | grep kvmfr || echo "no denials"

# libvirt didn't error out:
sudo journalctl -u virtqemud --since '1 minute ago' | grep -iE 'kvmfr|error'
```

Inside Windows: the IVSHMEM device should appear under **Device Manager → System devices** with the Looking Glass driver loaded.

On the host: launch `looking-glass-client` with `-f /dev/kvmfr0` — the `looking-glass-client` RPM ships dedicated `Kvmfr` and `Fullscreen + kvmfr` desktop actions for GNOME search. Once the client connects, the kvmfr refcount climbs and `lsof /dev/kvmfr0` shows both `qemu` and `looking-glass-client` holding it.

## Rollback or temporary swap

The cutover is fully reversible, in two flavors:

| Path | When you want it | What changes |
|---|---|---|
| **Temporary swap** | Quickly test if a problem is kvmfr-specific, or pause kvmfr without touching packages | VM XML only |
| **Full uninstall** | Stop using kvmfr indefinitely; minimise host footprint | XML + dnf remove + optional `qemu.conf` revert |

In both cases the VM must be shut down before the XML changes; `/dev/shm/looking-glass` is recreated automatically by libvirt at VM start (no manual `mkfifo`/`dd`).

### Temporary swap (XML only)

The cleanest workflow is to keep **two named XML files** — one for each backing — and `virsh define` whichever you want:

```
~/win11-system-shmem.xml      # <shmem name='looking-glass'> block
~/win11-system-kvmfr.xml      # <qemu:commandline> + memory-backend-file /dev/kvmfr0
```

Both are produced as a side-effect of the [cutover steps](#2-switch-the-vms-ivshmem-backing-from-devshm-to-devkvmfr0) above. If you only have one, dump the active one with `sudo virsh dumpxml win11-system > <file>` and hand-edit the other from the diff.

Flip between them:

```bash
sudo virsh shutdown win11-system && sleep 5
sudo virsh define ~/win11-system-shmem.xml      # or -kvmfr.xml
sudo virsh start win11-system
```

That's the entire procedure for a temporary swap — three commands, no uninstall, no system-wide changes. After the swap:

| Component | State when not using kvmfr |
|---|---|
| `kvmfr` module | Stays loaded, refcount drops to 0 — idle, ~24 KiB of kernel memory |
| `/dev/kvmfr0` | Still exists, no process opens it |
| `cgroup_device_acl` entry in `qemu.conf` | Whitelists a present device — harmless |
| SELinux `kvmfr` policy | File-context rule applies only to `/dev/kvmfr*` — no other effect |
| `modules-load.d` autoload | Keeps reloading at boot — harmless |
| LG client kvmfr desktop actions | Fail silently against missing/unused device — default launcher still works |

Coming back to kvmfr is symmetric — same three commands with the kvmfr XML.

### Full uninstall

Do the **temporary swap** above first to get the VM off `/dev/kvmfr0`. With the VM either stopped or running on `/dev/shm`, continue with the following.

#### (optional) Revert the `cgroup_device_acl` edit

The addition to `/etc/libvirt/qemu.conf` whitelisting `/dev/kvmfr0` is harmless to leave in place — it simply allows a device that won't exist after uninstall. For a clean revert, restore the backup created when the ACL was first added and reload the daemon:

```bash
sudo cp /etc/libvirt/qemu.conf.bak.<timestamp> /etc/libvirt/qemu.conf
sudo systemctl restart virtqemud
```

#### Remove the kvmfr packages

```bash
sudo dnf remove \
    akmod-kvmfr \
    kmod-kvmfr \
    'kmod-kvmfr-*.fc*' \
    kvmfr-kmod-common \
    kvmfr-kmod-selinux
```

Package scriptlets clean up automatically:

- `/lib/modules/<kver>/extra/kvmfr/kvmfr.ko.xz` deleted
- SELinux policy `kvmfr` removed via `semodule -r kvmfr` (in `%postun`)
- `/dev/kvmfr0`'s `kvmfr_device_t` label mapping removed; the device itself disappears when the module is unloaded
- `/usr/lib/modprobe.d/kvmfr.conf`, `/usr/lib/udev/rules.d/99-kvmfr.rules`, `/usr/lib/modules-load.d/kvmfr.conf` all removed

#### Unload the running module

```bash
sudo modprobe -r kvmfr
ls /dev/kvmfr0    # expect: No such file or directory
```

Requires refcount 0 (VM down + LG client closed). If `modprobe -r` refuses with `Module kvmfr is in use`, find what's holding it (`sudo lsof /dev/kvmfr0`) and close that first.

#### (optional) Remove the kvmfr desktop actions

The `Kvmfr` and `Fullscreen + kvmfr` actions in `looking-glass-client.desktop` will fail silently against the now-missing device. They're harmless, but to clean them up:

1. Delete the `Kvmfr;KvmfrFullscreen;` entries from the `Actions=` line in `looking-glass-client.desktop`
2. Remove the `[Desktop Action Kvmfr]` and `[Desktop Action KvmfrFullscreen]` sections
3. Bump `looking-glass-client.spec`, rebuild, reinstall

#### TL;DR — full uninstall in one block

```bash
sudo virsh shutdown win11-system && sleep 5
sudo virsh define ~/win11-system-shmem.xml
sudo dnf remove akmod-kvmfr kmod-kvmfr 'kmod-kvmfr-*.fc*' \
    kvmfr-kmod-common kvmfr-kmod-selinux
sudo modprobe -r kvmfr
sudo virsh start win11-system
```

About 30 seconds plus VM boot. Coming back to kvmfr is the symmetric opposite: reinstall the akmod packages, redo the XML cutover described in [Manual host configuration](#2-switch-the-vms-ivshmem-backing-from-devshm-to-devkvmfr0), restart the VM.

## Layout reference

```
/usr/lib/modprobe.d/kvmfr.conf                       # static_size_mb=256
/usr/lib/udev/rules.d/99-kvmfr.rules                 # owner/group/mode for /dev/kvmfr0
/usr/lib/modules-load.d/kvmfr.conf                   # boot-time autoload
/usr/share/selinux/packages/kvmfr.pp                 # SELinux policy module
/usr/share/licenses/kvmfr-kmod-common/LICENSE        # upstream GPL2
/lib/modules/<kver>/extra/kvmfr/kvmfr.ko.xz          # kernel module (built by akmods on the host)
/usr/src/akmods/looking-glass-kvmfr-kmod-*.src.rpm   # source for akmods rebuilds
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
