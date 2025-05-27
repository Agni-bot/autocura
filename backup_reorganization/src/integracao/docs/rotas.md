# Rotas

Este documento descreve as rotas disponíveis no módulo de integração.

## 🔐 Autenticação

### Login

```python
@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    security: SecurityConfig = Depends(get_security_config)
):
    """
    Autentica um usuário e retorna um token de acesso.
    
    Args:
        form_data: Dados do formulário de login
        security: Configuração de segurança
        
    Returns:
        Token: Token de acesso e refresh
        
    Raises:
        HTTPException: Se as credenciais forem inválidas
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(
        data={"sub": user.email}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
```

### Refresh Token

```python
@router.post("/auth/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Depends(get_refresh_token),
    security: SecurityConfig = Depends(get_security_config)
):
    """
    Atualiza um token de acesso usando o refresh token.
    
    Args:
        refresh_token: Token de atualização
        security: Configuração de segurança
        
    Returns:
        Token: Novo token de acesso
        
    Raises:
        HTTPException: Se o refresh token for inválido
    """
    try:
        payload = security.verify_token(refresh_token)
        user = await get_user_by_email(payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não encontrado"
            )
            
        access_token = security.create_access_token(
            data={"sub": user.email}
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido"
        )
```

## 📨 Mensagens

### Enviar Mensagem

```python
@router.post("/messages", response_model=Mensagem)
async def send_message(
    message: Mensagem,
    current_user: Usuario = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """
    Envia uma mensagem para processamento.
    
    Args:
        message: Mensagem a ser enviada
        current_user: Usuário atual
        message_service: Serviço de mensagens
        
    Returns:
        Mensagem: Mensagem enviada com status atualizado
        
    Raises:
        HTTPException: Se houver erro no processamento
    """
    try:
        return await message_service.send(message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
```

### Obter Mensagem

```python
@router.get("/messages/{message_id}", response_model=Mensagem)
async def get_message(
    message_id: str,
    current_user: Usuario = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """
    Obtém uma mensagem pelo ID.
    
    Args:
        message_id: ID da mensagem
        current_user: Usuário atual
        message_service: Serviço de mensagens
        
    Returns:
        Mensagem: Mensagem encontrada
        
    Raises:
        HTTPException: Se a mensagem não for encontrada
    """
    message = await message_service.get(message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensagem não encontrada"
        )
    return message
```

### Listar Mensagens

```python
@router.get("/messages", response_model=List[Mensagem])
async def list_messages(
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[TipoMensagem] = None,
    status: Optional[StatusMensagem] = None,
    current_user: Usuario = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    """
    Lista mensagens com filtros opcionais.
    
    Args:
        skip: Número de mensagens para pular
        limit: Limite de mensagens por página
        tipo: Filtrar por tipo de mensagem
        status: Filtrar por status
        current_user: Usuário atual
        message_service: Serviço de mensagens
        
    Returns:
        List[Mensagem]: Lista de mensagens
    """
    return await message_service.list(
        skip=skip,
        limit=limit,
        tipo=tipo,
        status=status
    )
```

## 📊 Monitoramento

### Métricas

```python
@router.get("/metrics", response_model=List[Metrica])
async def get_metrics(
    nome: Optional[str] = None,
    tipo: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: Usuario = Depends(get_current_user),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """
    Obtém métricas com filtros opcionais.
    
    Args:
        nome: Filtrar por nome da métrica
        tipo: Filtrar por tipo
        start_time: Data inicial
        end_time: Data final
        current_user: Usuário atual
        metrics_service: Serviço de métricas
        
    Returns:
        List[Metrica]: Lista de métricas
    """
    return await metrics_service.get_metrics(
        nome=nome,
        tipo=tipo,
        start_time=start_time,
        end_time=end_time
    )
```

### Alertas

```python
@router.get("/alerts", response_model=List[Alerta])
async def get_alerts(
    severidade: Optional[str] = None,
    resolvido: Optional[bool] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: Usuario = Depends(get_current_user),
    alert_service: AlertService = Depends(get_alert_service)
):
    """
    Obtém alertas com filtros opcionais.
    
    Args:
        severidade: Filtrar por severidade
        resolvido: Filtrar por status de resolução
        start_time: Data inicial
        end_time: Data final
        current_user: Usuário atual
        alert_service: Serviço de alertas
        
    Returns:
        List[Alerta]: Lista de alertas
    """
    return await alert_service.get_alerts(
        severidade=severidade,
        resolvido=resolvido,
        start_time=start_time,
        end_time=end_time
    )
```

## 🔄 WebSocket

### Conexão WebSocket

```python
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    current_user: Usuario = Depends(get_current_user_ws),
    ws_service: WebSocketService = Depends(get_ws_service)
):
    """
    Estabelece uma conexão WebSocket para eventos em tempo real.
    
    Args:
        websocket: Conexão WebSocket
        current_user: Usuário atual
        ws_service: Serviço WebSocket
        
    Raises:
        WebSocketDisconnect: Se a conexão for fechada
    """
    await ws_service.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_service.broadcast(data)
    except WebSocketDisconnect:
        await ws_service.disconnect(websocket)
```

## 📝 Exemplo de Uso

```python
import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"
TOKEN = "seu-token-aqui"

# Headers
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Enviar mensagem
mensagem = {
    "id": "123",
    "tipo": "evento",
    "origem": "monitoramento",
    "destino": "diagnostico",
    "payload": {
        "cpu_usage": 85.5,
        "memory_usage": 70.2
    }
}

response = requests.post(
    f"{BASE_URL}/messages",
    headers=headers,
    json=mensagem
)

# Obter métricas
params = {
    "nome": "cpu_usage",
    "start_time": datetime.utcnow().isoformat(),
    "end_time": datetime.utcnow().isoformat()
}

response = requests.get(
    f"{BASE_URL}/metrics",
    headers=headers,
    params=params
)

# WebSocket
import websockets
import asyncio

async def connect_ws():
    uri = f"ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Mensagem recebida: {message}")

asyncio.get_event_loop().run_until_complete(connect_ws())
```

## 📚 Referências

- [FastAPI Routing](https://fastapi.tiangolo.com/tutorial/routing/)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Requests](https://docs.python-requests.org/)
- [Python WebSockets](https://websockets.readthedocs.io/) 