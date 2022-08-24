#!/bin/bash
set -eu

# Set root password: WA7NERURoVlDegBUVyM1Kk
sed -i 's|root:\*:|root:$y$j9T$Qeof7nTZR1kT1cFwdlZqd0$B5.LdYzAcE8IwmEjeOUR9RwIwpalyyj/oxaiDqnryZ/:|' mnt/etc/shadow

# Speed up system
sed -i 's|"1"|"0"|'             mnt/etc/apt/apt.conf.d/20auto-upgrades
sed -i 's|WAIT=10|WAIT=1|'      mnt/etc/default/pollinate
sed -i 's|enabled=1|enabled=0|' mnt/etc/default/apport

touch mnt/etc/cloud/cloud-init.disabled
cp -v files/netplan.yaml mnt/etc/netplan/config.yaml

rm -v mnt/etc/systemd/system/dbus-org.freedesktop.ModemManager1.service
rm -v mnt/etc/systemd/system/multi-user.target.wants/ModemManager.service

# Set hostname
echo ibm > mnt/etc/hostname

# Set up ssh access
mkdir -p mnt/root/.ssh
cat files/id_rsa.pub >> mnt/root/.ssh/authorized_keys
chown root.root mnt/root/.ssh mnt/root/.ssh/authorized_keys
chmod go-rwx mnt/root/.ssh mnt/root/.ssh/authorized_keys
sed -i 's/^#PermitRootLogin/PermitRootLogin/' mnt/etc/ssh/sshd_config

# Copy pre-compiled service and systemd unit inside
cp -v files/crs mnt/root/crs
cp -v files/crs.service mnt/etc/systemd/system/crs.service
ln -s mnt/etc/systemd/system/crs.service mnt/etc/systemd/system/multi-user.target.wants/crs.service

# Ensure ssh host keys are generated during first boot
cp -v files/rc.local mnt/etc/rc.local

echo "Prepare image done. Now you may unmount it."
