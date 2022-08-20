FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /app

COPY ./src/ /app/
RUN dotnet publish -c release -o ./out


FROM mcr.microsoft.com/dotnet/aspnet:6.0
WORKDIR /app

RUN adduser -u 1000 --system --home /app --shell /usr/sbin/nologin --no-create-home --disabled-password usr
RUN apt-get update && apt-get install -y libgdiplus

ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 COMPlus_JitTelemetry=0 COMPlus_legacyCorruptedStateExceptionsPolicy=1 COMPlus_legacyUnhandledExceptionPolicy=1 ASPNETCORE_ENVIRONMENT=Production LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

COPY ./start.sh .
COPY --from=build /app/out/ /app/

RUN mkdir -p /app/data && mkdir -p /app/settings
VOLUME /app/data

CMD ["./start.sh"]
