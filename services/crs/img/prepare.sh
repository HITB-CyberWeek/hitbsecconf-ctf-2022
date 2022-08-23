#!/bin/bash
set -eu

# Set root password: WA7NERURoVlDegBUVyM1Kk
sed -i 's|root:\*:|root:$y$j9T$Qeof7nTZR1kT1cFwdlZqd0$B5.LdYzAcE8IwmEjeOUR9RwIwpalyyj/oxaiDqnryZ/:|' mnt/etc/shadow

# Speed up system
sed -i 's|"1"|"0"|' mnt/etc/apt/apt.conf.d/20auto-upgrades
touch mnt/etc/cloud/cloud-init.disabled

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

echo "Prepare image done. Now you may unmount it."
