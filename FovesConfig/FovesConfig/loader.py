import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Type

from pydantic import BaseModel

# 落盘重试：Windows 上目标文件正被别的进程读时 os.replace 会抛 PermissionError，
# 并发读压力下实测 81% 的写入都要重试，所以这里必须等，不能失败就走。
_WRITE_ATTEMPTS = 100  # 最大写入重试次数
_WRITE_RETRY_DELAY = 0.005  # 重试延时
_WRITE_WARN_EVERY = 10  # 每 10 次重试警告
# 读取重试：读者也可能正好撞上别人 replace 的瞬间。
_READ_ATTEMPTS = 6  # 最大重试
_READ_RETRY_DELAY = 0.005  # 重试延时


def _default_file_mode() -> int:
    """按当前 umask 算出新建文件该有的权限位（mkstemp 建出来的是 0600，太紧）。"""
    umask = os.umask(0)
    os.umask(umask)
    return 0o666 & ~umask


def _atomic_write_text(path: Path, text: str) -> None:
    """先写同目录临时文件再 os.replace 顶掉目标：读者要么看到旧内容，要么看到新内容。"""
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
            file.write(text)
            file.flush()
            os.fsync(file.fileno())
        # 换了新 inode 会丢掉原文件的权限位，这里对齐回去。
        try:
            if path.exists():
                shutil.copymode(path, tmp)
            else:
                os.chmod(tmp, _default_file_mode())
        except OSError:
            pass
        last_error: PermissionError | None = None
        for attempt in range(1, _WRITE_ATTEMPTS + 1):
            try:
                os.replace(tmp, path)
                return
            except PermissionError as error:
                last_error = error
                if attempt % _WRITE_WARN_EVERY == 0:
                    print(
                        f'[FovesConfig] 写入 {path} 第 {attempt} 次重试未成功（文件被占用？）：{error}',
                        file=sys.stderr,
                    )
                time.sleep(_WRITE_RETRY_DELAY)
        raise last_error or RuntimeError(f'写入 {path} 失败')
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def _read_text(path: Path) -> str:
    """读取文本，撞上别人正在替换文件的瞬间就稍等重试。"""
    last_error: PermissionError | None = None
    for _ in range(_READ_ATTEMPTS):
        try:
            return path.read_text("UTF8")
        except PermissionError as error:
            last_error = error
            time.sleep(_READ_RETRY_DELAY)
    raise last_error or RuntimeError(f'读取 {path} 失败')


class ConfigLoader[T: BaseModel]:
    def __init__(self, path: str|Path, model: Type[T]):
        self.path = Path(path)
        self.model_cls = model
    
    def _read(self):
        if self.path.exists():
            self.model = self.model_cls.model_validate_json(_read_text(self.path))
        else:
            self.model = self.model_cls()

    def _write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_text(
            self.path,
            self.model.model_dump_json(indent=2, ensure_ascii=False),
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
