# Dockerfile para o Módulo de Finanças

# Use uma imagem Python base leve
FROM python:3.9-slim

# Defina o diretório de trabalho no contêiner
WORKDIR /app

# Copie o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY ./requirements.txt /app/requirements.txt

# Instale as dependências
# É importante ter o MetaTrader5 como dependência opcional ou garantir que o ambiente de build
# possa lidar com sua ausência se ele não for instalável via pip diretamente (requer terminal MT5).
# Para este Dockerfile, assumimos que as dependências em requirements.txt são instaláveis via pip.
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação para o diretório de trabalho
COPY . /app/

# Defina variáveis de ambiente (exemplo, idealmente configuradas no runtime)
# ENV MT5_LOGIN="your_login"
# ENV MT5_PASSWORD="your_password"
# ENV MT5_SERVER="your_server"
ENV FLASK_APP=api.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# Exponha a porta que o Flask usará
EXPOSE 5001

# Comando para rodar a aplicação quando o contêiner iniciar
# O entrypoint pode ser um script que espera o MT5 estar pronto, se necessário.
CMD ["flask", "run"]
