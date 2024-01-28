# FROM --platform=${BUILDPLATFORM:-linux/amd64} golang:1.20 as builder

# FROM ghcr.io/hybridgroup/opencv:4.8.1 as builder
FROM gocv/opencv:4.8.0
# ENV GOPATH /go

ARG TARGETPLATFORM
ARG BUILDPLATFORM
ARG TARGETOS
ARG TARGETARCH

WORKDIR /app/
COPY go.mod go.sum ./

RUN go env -w GO111MODULE=on
RUN go mod download
RUN go mod verify

COPY . .

RUN GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build -a -ldflags='-w -s' -o streamer ./main.go

# FROM --platform=${TARGETPLATFORM:-linux/amd64} scratch
# WORKDIR /app/
# COPY --from=builder /app/streamer /app/streamer
ENTRYPOINT ["/app/streamer"]
