#!/bin/bash
set -eu
# Root password: WA7NERURoVlDegBUVyM1Kk
sed -i 's|root:\*:|root:$y$j9T$Qeof7nTZR1kT1cFwdlZqd0$B5.LdYzAcE8IwmEjeOUR9RwIwpalyyj/oxaiDqnryZ/:|' mnt/etc/shadow
cp -v files/crs mnt/root/crs
cp -v files/crs.service mnt/etc/systemd/system/crs.service
ln -s mnt/etc/systemd/system/crs.service mnt/etc/systemd/system/multi-user.target.wants/crs.service

echo "Prepare image done. Now you may unmount it."
