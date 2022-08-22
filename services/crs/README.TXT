CRS service binary runs inside VM (qemu).

To ssh into VM:

    ssh root@localhost -p2222

To see console logs:

    docker logs crs -f

To restart service (beware! boot may take several minutes):

    docker compose -f /home/crs/docker-compose.yml restart
