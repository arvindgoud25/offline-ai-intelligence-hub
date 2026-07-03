import json
from typing import Any

from llm.prompts import DOCUMENT_PROMPTS, GENERIC_EXTRACTION_PROMPT


class LLMBackend:
    name: str = ""
    available: bool = False
    model: str = ""

    def load(self) -> None:
        raise NotImplementedError

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class NoneBackend(LLMBackend):
    name = "None"

    def __init__(self) -> None:
        self.available = True

    def load(self) -> None:
        self.available = True

    def generate(self, prompt: str) -> str:
        return "{}"


class OllamaBackend(LLMBackend):
    name = "Ollama"

    def __init__(self, model: str = "llama3.2") -> None:
        self.model = model

    def load(self) -> None:
        try:
            import ollama
            resp = ollama.list()
            self.available = any(m.model == self.model or m.model.startswith(self.model + ":") for m in (resp.models or []))
        except Exception:
            self.available = False

    def generate(self, prompt: str) -> str:
        import ollama
        resp = ollama.generate(
            model=self.model,
            prompt=prompt,
            format="json",
            options={"num_predict": 2048, "temperature": 0.1},
        )
        return resp.response or ""


_backend: LLMBackend | None = None


def load_model(backend_name: str = "ollama", model: str = "llama3.2") -> None:
    global _backend
    if backend_name == "ollama":
        ob = OllamaBackend(model=model)
        ob.load()
        if ob.available:
            _backend = ob
            return
    _backend = NoneBackend()
    _backend.load()


def is_ready() -> bool:
    return _backend is not None and _backend.available and _backend.name != "None"


def get_active_backend() -> LLMBackend | None:
    return _backend


def get_backend_status() -> dict[str, Any]:
    if _backend is None:
        return {"name": "Not loaded", "available": False, "model": ""}
    return {
        "name": _backend.name,
        "available": _backend.available,
        "model": _backend.model if hasattr(_backend, "model") else "",
    }


def generate_structured_json(
    text: str,
    doc_type: str = "",
    schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not is_ready():
        raise RuntimeError("No LLM backend is loaded and ready.")
    prompt = DOCUMENT_PROMPTS.get(doc_type, GENERIC_EXTRACTION_PROMPT)
    if schema:
        prompt += f"\n\nExpected JSON structure:\n{json.dumps(schema, indent=2)}"
    full_prompt = f"{prompt}\n\nText:\n{text}"
    try:
        response = _backend.generate(full_prompt)
    except Exception:
        return {}
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return {}
        return {}
