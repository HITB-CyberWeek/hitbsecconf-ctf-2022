#/bin/bash

cd `dirname $0`/src/bin/Release/net6.0/publish >/dev/null 2>&1
exec dotnet smallwordchecker.dll "$@"
