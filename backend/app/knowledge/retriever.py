import re
from abc import ABC, abstractmethod
from pathlib import Path

_FAQ_DIR = Path(__file__).parent / "faq"
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
_STOP_WORDS = {"the", "a", "an", "to", "do", "i", "can", "how", "where", "is", "of", "my", "see", "in", "on"}


def _tokenize(text: str) -> set[str]:
    return {token for token in _TOKEN_PATTERN.findall(text.lower()) if token not in _STOP_WORDS}


class Retriever(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> list[str]: ...


class KeywordRetriever(Retriever):
    def __init__(self, faq_dir: Path = _FAQ_DIR) -> None:
        self.documents: list[tuple[str, set[str]]] = []
        for path in sorted(faq_dir.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            self.documents.append((content, _tokenize(content)))

    def search(self, query: str, top_k: int = 3) -> list[str]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []
        scored = []
        for content, document_tokens in self.documents:
            overlap = len(query_tokens & document_tokens)
            if overlap > 0:
                scored.append((overlap, content))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [content for _, content in scored[:top_k]]
