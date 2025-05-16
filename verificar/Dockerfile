# Dockerfile para RollbackOperator
FROM golang:1.20-alpine AS builder

WORKDIR /workspace
# Copiar os arquivos go.mod e go.sum
COPY go.mod go.mod
COPY go.sum go.sum
# Baixar dependências
# RUN go mod tidy
RUN go mod download

# Copiar o código-fonte
COPY main.go main.go
COPY api/ api/
COPY controller/ controller/

# Construir
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o manager main.go

# Imagem final
FROM alpine:latest
WORKDIR /
COPY --from=builder /workspace/manager .
# Adicionar um usuário não root é uma boa prática de segurança
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

ENTRYPOINT ["/manager"]

