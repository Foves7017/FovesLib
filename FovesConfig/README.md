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

### 读写行为

- **读取**：进入上下文管理器时，若文件存在则 `model_validate_json` 反序列化，否则用 `model_cls()` 构造默认实例。
- **写入**：退出上下文管理器时自动创建父目录，以 `indent=2`、`ensure_ascii=False` 写出 JSON。

### 其他
如果你发现自己需要手动调用 save() 或 exit()，请先考虑是否应该使用上下文管理器。大多数修改配置的场景都更适合：

```Python
with ConfigLoader(...) as config:
    ...
```

而不是手动管理配置对象的生命周期。