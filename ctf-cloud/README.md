# ctf-cloud
Scripts for deploying VPN and cloud console hosts. These hosts are parts of CTF infrastructure.

The VPN is a host which routes all team traffic on CTF, teams' routers connect to it using OpenVPN, thats why it called VPN. The checksystem also uses this host to access the teams.

The cloud control panel provides web-interface for participants to create their vulnerable image and control it: take snapshots, reboot an so on. In addition to vulnerable image, the team router is created for every team, which connects the team network to the central VPN host. Cloud console gives participant an OpenVPN config to connect to this team router.

![Network scheme](https://conference.hitb.org/hitbsecconf2021sin/wp-content/uploads/sites/12/2021/07/pasted-image-0.png)

## Preparations Steps ##

VMs for teams are created in Digital Ocean, so before the start, you should register on this site.

## Deployment Steps ##

At first, the VPN should be deployed. After VPN is deployed, the Cloud console should be deployed. Instructions can be found in [./vpn](./vpn) and [./cloud](./cloud) dirs.

For whole deployment proccess it is recommended to use some Linux host.
