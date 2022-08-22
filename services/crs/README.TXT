CRS service binary runs inside VM (qemu).

To see console logs:

    docker logs crs -f

To ssh into VM:

    ssh root@localhost -p2222

To restart service (beware! boot may take several minutes):

    docker compose restart
