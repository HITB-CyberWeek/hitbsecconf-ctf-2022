#!/bin/sh

chown usr: /app/data /app/settings
chmod -R 755 /app /app/wwwroot
chmod 700 /app/data

su usr -s /bin/sh -c 'dotnet smallword.dll'
