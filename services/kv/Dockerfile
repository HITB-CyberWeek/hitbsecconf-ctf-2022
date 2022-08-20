FROM golang:1.19-alpine

ENV GOFLAGS="-mod=vendor"
ADD . /app
WORKDIR /app

RUN go build

EXPOSE 3000
ENTRYPOINT ["/app/kv"]
