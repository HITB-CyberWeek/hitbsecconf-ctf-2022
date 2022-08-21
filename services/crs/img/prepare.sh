#!/bin/bash
set -eu

# Set root password: WA7NERURoVlDegBUVyM1Kk
sed -i 's|root:\*:|root:$y$j9T$Qeof7nTZR1kT1cFwdlZqd0$B5.LdYzAcE8IwmEjeOUR9RwIwpalyyj/oxaiDqnryZ/:|' mnt/etc/shadow

# Speed up system
sed -i 's|"1"|"0"|' mnt/etc/apt/apt.conf.d/20auto-upgrades

for unit in \
        snapd.service \
        cloud-init.service \
        cloud-init-local.service \
        apport.service \
        apparmor.service \
        ssh.service \
        snapd.apparmor.service \
        unattended-upgrades.service \
        systemd-timesyncd.service \
        lvm2-monitor.service \
        ModemManager.service \
        remote-fs-pre.target \
        e2scrub_all.timer \
        systemd-tmpfiles-clean.timer \
        fstrim.timer \
        man-db.timer \
        fwupd-refresh.timer \
        apt-daily-upgrade.timer \
        apt-daily.timer
do
    ln -s /dev/null mnt/etc/systemd/system/$unit
    echo "Disabled: $unit"
done

# Set hostname
echo ibm > mnt/etc/hostname

# Copy pre-compiled service and systemd unit inside
cp -v files/crs mnt/root/crs
cp -v files/crs.service mnt/etc/systemd/system/crs.service
ln -s mnt/etc/systemd/system/crs.service mnt/etc/systemd/system/multi-user.target.wants/crs.service

echo "Prepare image done. Now you may unmount it."
