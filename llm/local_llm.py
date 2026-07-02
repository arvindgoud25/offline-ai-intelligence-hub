from typing import Any

from llm.prompts import DOCUMENT_PROMPTS, GENERIC_EXTRACTION_PROMPT
from schemas import DOCUMENT_SCHEMAS


class LLMBackend:
    name: str = ""
    available: bool = False

    def load(self) -> None:
        raise NotImplementedError

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OllamaBackend(LLMBackend):
    name = "Ollama"

    def __init__(self, model: str = "llama3") -> None:
        self.model = model

    def load(self) -> None:
        try:
            import ollama
            ollama.list()
            self.available = True
        except Exception:
            self.available = False

    def generate(self, prompt: str) -> str:
        import ollama
        resp = ollama.generate(model=self.model, prompt=prompt)
        return resp.get("response", "")


class LlamaCppBackend(LLMBackend):
    name = "llama.cpp"

    def __init__(self, model_path: str = "") -> None:
        self.model_path = model_path

    def load(self) -> None:
        try:
            from llama_cpp import Llama
            self._model = Llama(model_path=self.model_path)
            self.available = True
        except Exception:
            self.available = False

    def generate(self, prompt: str) -> str:
        resp = self._model(prompt, max_tokens=2048)
        return resp["choices"][0]["text"]


_backend: LLMBackend | None = None


def get_available_backends() -> list[LLMBackend]:
    backends: list[LLMBackend] = []
    try:
        ob = OllamaBackend()
        ob.load()
        backends.append(ob)
    except Exception:
        pass
    return backends


def load_model(backend: LLMBackend) -> None:
    global _backend
    backend.load()
    _backend = backend


def is_ready() -> bool:
    return _backend is not None and _backend.available


def get_active_backend() -> LLMBackend | None:
    return _backend


def generate_structured_json(
    text: str,
    doc_type: str = "",
    schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not is_ready():
        raise RuntimeError("No LLM backend is loaded and ready.")
    prompt = DOCUMENT_PROMPTS.get(doc_type, GENERIC_EXTRACTION_PROMPT)
    full_prompt = f"{prompt}\n\nText:\n{text}"
    response = _backend.generate(full_prompt)
    import json
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("LLM output could not be parsed as JSON.")
