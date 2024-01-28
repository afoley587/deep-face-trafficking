# FROM --platform=${BUILDPLATFORM:-linux/amd64} golang:1.20 as builder

FROM ghcr.io/hybridgroup/opencv:4.8.1 as builder

ENV GOPATH /go

ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETOS
ARG TARGETARCH

WORKDIR /app/
ADD . .
RUN GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build -ldflags="-w -s" -o streamer

# FROM --platform=${TARGETPLATFORM:-linux/amd64} scratch
# WORKDIR /app/
# COPY --from=builder /app/streamer /app/streamer
ENTRYPOINT ["/app/streamer"]
