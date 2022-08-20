#!/bin/bash
set -eu
sed -i 's|root:\*:|root:$6$Yyhk9NIw$4UNfl90BPSlx6usPZoc8Phj3u2YB67XnXA6jnrBOcVf2N5ioEVLb5EApefmNJGAk2Jn8WeRRH8ZM6Ns8BLVsw.:|' mnt/etc/shadow
cp -v files/crs mnt/root/crs
cp -v files/crs.service mnt/etc/systemd/system/crs.service
ln -s mnt/etc/systemd/system/crs.service mnt/etc/systemd/system/multi-user.target.wants/crs.service

echo "Prepare image done. Now you may unmount it."
