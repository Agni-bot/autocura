FROM golang:1.18 as builder

WORKDIR /workspace

# Copiar arquivos Go Modules
COPY go.mod go.sum ./
RUN go mod download

# Copiar o código-fonte
COPY . .

# Compilar
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o manager main.go

FROM gcr.io/distroless/static:nonroot
WORKDIR /
COPY --from=builder /workspace/manager .
USER 65532:65532

ENTRYPOINT ["/manager"]
