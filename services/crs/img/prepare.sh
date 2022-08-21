#!/bin/bash
set -eu

# Set root password: WA7NERURoVlDegBUVyM1Kk
sed -i 's|root:\*:|root:$y$j9T$Qeof7nTZR1kT1cFwdlZqd0$B5.LdYzAcE8IwmEjeOUR9RwIwpalyyj/oxaiDqnryZ/:|' mnt/etc/shadow

# Speed up system
sed -i 's|"1"|"0"|' mnt/etc/apt/apt.conf.d/20auto-upgrades

ln -s /dev/null mnt/etc/systemd/system/snapd.service
ln -s /dev/null mnt/etc/systemd/system/cloud-init.service
ln -s /dev/null mnt/etc/systemd/system/apport.service
ln -s /dev/null mnt/etc/systemd/system/apparmor.service
ln -s /dev/null mnt/etc/systemd/system/ssh.service
ln -s /dev/null mnt/etc/systemd/system/snapd.apparmor.service
ln -s /dev/null mnt/etc/systemd/system/unattended-upgrades.service
ln -s /dev/null mnt/etc/systemd/system/ModemManager.service

ln -s /dev/null mnt/etc/systemd/system/e2scrub_all.timer
ln -s /dev/null mnt/etc/systemd/system/systemd-tmpfiles-clean.timer
ln -s /dev/null mnt/etc/systemd/system/fstrim.timer
ln -s /dev/null mnt/etc/systemd/system/man-db.timer
ln -s /dev/null mnt/etc/systemd/system/fwupd-refresh.timer
ln -s /dev/null mnt/etc/systemd/system/apt-daily-upgrade.timer
ln -s /dev/null mnt/etc/systemd/system/apt-daily.timer

# Copy pre-compiled service and systemd unit inside
cp -v files/crs mnt/root/crs
cp -v files/crs.service mnt/etc/systemd/system/crs.service
ln -s mnt/etc/systemd/system/crs.service mnt/etc/systemd/system/multi-user.target.wants/crs.service

echo "Prepare image done. Now you may unmount it."
