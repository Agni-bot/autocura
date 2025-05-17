FROM golang:1.18-alpine AS builder

WORKDIR /workspace

# Copiar arquivos Go Modules
COPY go.mod go.sum ./
RUN go mod download

# Copiar todo o código-fonte para o caminho esperado pelo Go
RUN mkdir -p /go/src/autocura && \
    cp -r . /go/src/autocura/RollbackOperator && \
    cp -r api controllers /go/src/autocura/RollbackOperator/

WORKDIR /go/src/autocura/RollbackOperator

# Compilar
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o /workspace/rollback-operator .

# Imagem final
FROM alpine:3.16

WORKDIR /
COPY --from=builder /workspace/rollback-operator .
USER 65532:65532

ENTRYPOINT ["/rollback-operator"]
