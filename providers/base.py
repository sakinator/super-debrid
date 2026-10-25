from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class FileEntry(BaseModel):
    id: str
    name: str
    size: int = 0
    download_url: Optional[str] = None
    stream_url: Optional[str] = None

class ResolveResult(BaseModel):
    success: bool
    provider: str
    title: str = "Stream"
    original_url: str
    stream_url: Optional[str] = None
    download_url: Optional[str] = None
    size: int = 0
    cached: bool = False
    mime_type: Optional[str] = None
    is_streamable: bool = True
    error: Optional[str] = None
    files: List[FileEntry] = []
    metadata: Dict[str, Any] = {}

class BaseFreeProvider(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def is_free(self) -> bool:
        return True

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Returns True if this provider can handle the given URL or magnet."""
        pass

    @abstractmethod
    async def resolve(self, url: str, **kwargs) -> ResolveResult:
        """Resolves the given link or magnet into an unthrottled direct stream link."""
        pass

    async def check_cache(self, identifier: str) -> bool:
        """Optional cache probe (returns True if file is already cached on cloud)."""
        return False

    async def get_status(self) -> Dict[str, Any]:
        """Returns provider health, free tier limits, or account status."""
        return {"id": self.id, "name": self.name, "online": True}
