from typing import Type
from pathlib import Path
from pydantic import BaseModel

class ConfigLoader[T: BaseModel]:
    def __init__(self, path: str|Path, model: Type[T]):
        self.path = Path(path)
        self.model_cls = model
    
    def _read(self):
        if self.path.exists():
            self.model = self.model_cls.model_validate_json(self.path.read_text("UTF8"))
        else:
            self.model = self.model_cls()

    def _write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            self.model.model_dump_json(indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        
    def readonly(self) -> T:
        self._read()
        return self.model
    
    def overwrite(self, model: T) -> T:
        self.model = model
        self._write()
        return self.model

    def __enter__(self) -> T:
        self._read()
        return self.model

    def __exit__(self, exc_type, exc, tb):
        self._write()
