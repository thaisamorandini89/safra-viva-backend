"""Cliente do Google Gemini isolado do restante do agente (troca de provedor fica restrita a este módulo)."""
import os

MODELO_PADRAO = 'gemini-3.5-flash-lite'
MAX_RODADAS = 4


class ErroLLM(Exception):
    def __init__(self, mensagem, status=502):
        super().__init__(mensagem)
        self.status = status


class ClienteGemini:
    def __init__(self, api_key=None, modelo=None, timeout_s=None):
        from google import genai
        from google.genai import types

        self._types = types
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ErroLLM('GEMINI_API_KEY não configurada no backend.', status=503)
        self.modelo = modelo or os.environ.get('SAFRAIA_MODEL', MODELO_PADRAO)
        timeout_s = float(timeout_s or os.environ.get('SAFRAIA_TIMEOUT', 30))
        self._client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=int(timeout_s * 1000)),
        )

    def conversar(self, sistema, pergunta, declaracoes, executar):
        """Executa o laço de function calling.

        declaracoes: {nome: {'descricao', 'parametros'}}; executar(nome, args) -> dict.
        Retorna (texto_final, [(nome, args, resultado), ...]).
        """
        from google.genai import errors

        types = self._types
        funcoes = [
            types.FunctionDeclaration(name=nome, description=d['descricao'],
                                      parameters_json_schema=d['parametros'])
            for nome, d in declaracoes.items()
        ]
        config = types.GenerateContentConfig(
            system_instruction=sistema,
            tools=[types.Tool(function_declarations=funcoes)] if funcoes else None,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            temperature=0.2,
        )
        conteudo = [types.Content(role='user', parts=[types.Part.from_text(text=pergunta)])]
        chamadas = []
        try:
            for _ in range(MAX_RODADAS):
                resposta = self._client.models.generate_content(
                    model=self.modelo, contents=conteudo, config=config)
                pedidos = resposta.function_calls or []
                if not pedidos:
                    return (resposta.text or '').strip(), chamadas
                conteudo.append(resposta.candidates[0].content)
                partes = []
                for fc in pedidos:
                    args = dict(fc.args or {})
                    resultado = executar(fc.name, args)
                    chamadas.append((fc.name, args, resultado))
                    partes.append(types.Part.from_function_response(name=fc.name, response=resultado))
                conteudo.append(types.Content(role='user', parts=partes))
            raise ErroLLM('O assistente não concluiu a resposta. Tente reformular a pergunta.')
        except ErroLLM:
            raise
        except errors.APIError as exc:
            if getattr(exc, 'code', None) == 429:
                raise ErroLLM('Limite de uso do Gemini atingido. Aguarde alguns instantes.', status=429) from exc
            raise ErroLLM('Falha ao consultar o Gemini. Tente novamente.') from exc
        except Exception as exc:  # timeout/rede
            raise ErroLLM('O Gemini não respondeu a tempo. Tente novamente.', status=504) from exc
