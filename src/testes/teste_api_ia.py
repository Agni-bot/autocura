import os
import openai
from dotenv import load_dotenv
import json
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

def testar_conexao_api():
    try:
        # Configurar a API
        client = openai.OpenAI(
            api_key=os.getenv('AI_API_KEY'),
            base_url=os.getenv('AI_API_ENDPOINT')
        )
        
        # Testar uma chamada simples
        response = client.chat.completions.create(
            model=os.getenv('AI_API_PRIMARY_MODEL'),
            messages=[
                {"role": "system", "content": "Você é um assistente de teste para o sistema de autocura."},
                {"role": "user", "content": "Teste de conexão com a API."}
            ],
            max_tokens=50
        )
        
        # Registrar o resultado
        resultado = {
            "data": datetime.now().isoformat(),
            "status": "sucesso",
            "modelo": os.getenv('AI_API_PRIMARY_MODEL'),
            "resposta": response.choices[0].message.content
        }
        
        # Salvar resultado no arquivo de memória
        with open('memoria_compartilhada.json', 'r+', encoding='utf-8') as f:
            memoria = json.load(f)
            memoria['log_eventos'].append({
                "data": resultado["data"],
                "evento": "Teste de conexão com API de IA",
                "detalhes": f"Status: {resultado['status']}, Modelo: {resultado['modelo']}"
            })
            f.seek(0)
            json.dump(memoria, f, indent=2, ensure_ascii=False)
            f.truncate()
        
        print("✅ Teste de conexão com a API realizado com sucesso!")
        print(f"Resposta: {resultado['resposta']}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar conexão com a API: {str(e)}")
        return False

if __name__ == "__main__":
    testar_conexao_api() 