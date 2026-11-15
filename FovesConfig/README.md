# FovesConfig

基于 Pydantic 的配置管理工具，上下文管理器自动读写 JSON 配置文件。

可使用 pip 安装或下载源码使用：
```BASH
pip install FovesConfig
```

项目主页：
https://github.com/Foves7017/FovesLib

## ConfigLoader

泛型配置加载器。把你的配置定义成一个 Pydantic 模型，然后用 `ConfigLoader` 包裹它——进入上下文自动读取 JSON，退出时自动写回，省去所有手工序列化的麻烦。

### 基本用法

```Python
from pydantic import BaseModel
from FovesConfig import ConfigLoader

class AppConfig(BaseModel):
    host: str = "localhost"
    port: int = 8080
    debug: bool = False

with ConfigLoader("config.json", AppConfig) as cfg:
    print(cfg.host)   # 首次运行会使用默认值
    cfg.port = 9090   # 修改配置
# 退出上下文时自动写入 config.json
```

### 参数

`path: str | Path` — 配置文件路径。文件存在则读取，不存在则使用模型默认值。

`model: Type[T]` — 一个 Pydantic BaseModel 子类，定义了配置的结构和默认值。

### 只读
你可以使用如下的方法只读取磁盘上的配置，在此例中，就算修改 cfg 的值也不会同步到磁盘中。

```Python
loader = ConfigLoader("config.json", AppConfig)
cfg = loader.readonly()
print(cfg.host)
```

### 覆盖写入

不想进上下文、只想把一份新配置整体写回去时，用 `overwrite()`：调用即落盘，并把这个实例返回给你。
一个典型用法（也是我创建这个方法的原因）就是在配置初始化时创建文件。

```Python
loader = ConfigLoader("config.json", AppConfig)
cfg = loader.overwrite(AppConfig(port=9090))
```

- **写入时机**：调用时立刻写，不需要等 `with` 块退出；父目录不存在会自动递归创建。
- **不会先读取**：所以磁盘上是坏掉的 JSON 也能被直接覆盖。
- **不做校验**：入参必须是你在 `ConfigLoader` 上声明的那个模型实例。传 `dict`、`None` 之类会直接抛 `AttributeError`（它只会去调 `model_dump_json`）；传成别的模型也会被原样写出去。
- **和 `readonly()` 的关系**：`readonly()` 每次调用都会重新从磁盘读取，因此**以磁盘上最后一次写入的内容为准**。`overwrite()` 之后再 `readonly()`，拿到的是重新反序列化出来的新对象，不是你传进去的那个引用。

### 读写行为

- **读取**：进入上下文管理器时，若文件存在则 `model_validate_json` 反序列化，否则用 `model_cls()` 构造默认实例。
- **写入**：退出上下文管理器时自动创建父目录，以 `indent=2`、`ensure_ascii=False` 写出 JSON。
- **写入实现**：落盘逻辑集中在内部的 `_write()`，上下文退出和 `overwrite()` 共用同一套行为，两者格式完全一致。它写的是「同目录临时文件 → `os.replace`」，细节见下面的「并发与原子写」。
- **异常路径**：`__exit__` 不会吞掉异常，也不会因为异常就跳过写入——块内抛异常时配置依然会写回磁盘。

### 并发与原子写

写入不是「打开目标文件直接覆盖」，而是「先写同目录的临时文件，再 `os.replace` 顶掉目标」。所以另一个进程或线程在这个瞬间去读，要么读到旧内容，要么读到新内容，不会读到半截 JSON。

代价是 Windows 上 `os.replace` 撞上别人正打开着目标文件时会抛 `PermissionError`，因此读写都带短重试：

| | 每次间隔 | 上限 | 最坏耗时 |
|---|---|---|---|
| 写入（`os.replace`） | 5 ms | 100 次 | ~500 ms |
| 读取（`read_text`） | 5 ms | 6 次 | ~30 ms |

- 写入每满 10 次还没成功，会往 **`sys.stderr`** 打一条警告：
  `[FovesConfig] 写入 config.json 第 30 次重试未成功（文件被占用？）：[WinError 5] ...`
  故意不写 stdout——stdio 型 MCP 服务的 stdout 是协议通道，多打一行就会把协议打坏。
- 100 次全失败会抛出原始 `PermissionError`，同时删掉临时文件，不会留下半截目标文件。
- 临时文件形如 `config.json.a1b2c3.tmp`，与目标同目录（同目录才能保证 `os.replace` 是原子的）。进程被强杀时可能留下一个孤儿临时文件，不影响读取，可手动删。
- 这套重试只解决「读到半截」。多个进程同时改同一份配置时，后写的会覆盖先写的，`ConfigLoader` **不提供跨进程锁。**

### 其他
如果你发现自己需要手动调用 save() 或 exit()，请先考虑是否应该使用上下文管理器。大多数修改配置的场景都更适合：

```Python
with ConfigLoader(...) as config:
    ...
```

而不是手动管理配置对象的生命周期。

如果确实需要“不进上下文也要写盘”的场景（例如程序启动时生成一份默认配置、或把外部来源的配置整体落盘），直接用 `overwrite()` 就够了，不必自己造 `save()` / `exit()`。