FROM golang:1.18-alpine AS builder

WORKDIR /workspace

# Copiar arquivos Go Modules
COPY go.mod go.sum ./
RUN go mod download

# Copiar todo o código-fonte
COPY . .

# Configurar o módulo Go
ENV GO111MODULE=on
ENV GOPATH=/go
ENV PATH=$PATH:$GOPATH/bin

# Compilar
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -mod=readonly -a -o rollback-operator main.go

# Imagem final
FROM alpine:3.16

WORKDIR /
COPY --from=builder /workspace/rollback-operator .
USER 65532:65532

ENTRYPOINT ["/rollback-operator"]
