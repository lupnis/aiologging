# aiologging

！！该readme由copilot生成~~私密马赛🥺~~！！

> 最初是为了解决coloredlogs往日志文件里面塞ANSI控制字的问题，造了这个轮子

`aiologging` 模块实现了异步日志记录器，支持将日志同时输出到控制台和文件。模块内提供了对日志文本的样式美化功能，可使用 `Styled` 对象设置 ANSI 风格装饰。该模块同时提供ANSI字符和原生文本隔离，以避免在日志文件中混入不可读的ANSI控制字（默认为隔离状态，可设置为保留）

## 依赖环境

- Python 3.8 及以上版本
- 第三方库：`aiofiles`

## 简单使用

使用示例：
    
```python
# filepath: examples/usage.py
import asyncio
from middlewares.logs import Logger, Levels

async def main():
    logger = Logger()  # 使用默认配置
    await logger.info("这是一个信息日志")
    await logger.error("这是一个错误日志")

asyncio.run(main())
```

上述代码会创建一个默认配置的日志记录器，并分别记录信息和错误日志。

## Styled 使用用例

`Styled` 类用于为字符串添加 ANSI 样式，无论是直接输出或者格式化时，都无需手动调用 `.styled` 属性。例如：

```python
# filepath: examples/usage_styled.py
from middlewares.logs import Styled, Styles

# 直接将 Styled 对象作为字符串输出时，自动返回带 ANSI 转义码的文本
styled_message = Styled("警告：出现异常！", Styles.BOLD, Styles.RED)
print(styled_message)  

# 如果需要获取普通文本，可以使用 .plain 属性
print(styled_message.plain)
```

## Styles 类功能介绍

`Styles` 类定义了多种 ANSI 转义码，并提供了一些辅助函数：
- **ID_COLOR(id)**：根据颜色 ID (0-255) 生成 256 色模式的前景色 ANSI 代码。
- **ID_COLOR_BG(id)**：根据颜色 ID (0-255) 生成 256 色模式的背景颜色 ANSI 代码。
- **RGB_COLOR(r, g, b)**：根据 RGB 数值生成前景色的 ANSI 转义码。
- **RGB_COLOR_BG(r, g, b)**：根据 RGB 数值生成背景色的 ANSI 转义码。
- **make_color_prefix(code)**：生成单个 ANSI 转义码的前缀字符串。
- **make_colors_prefix(codes: Optional[List[Any]] = [])**：接收一系列 ANSI 代码，生成组合后的 ANSI 风格前缀字符串。

利用这些函数可以更灵活地构造自定义样式的日志输出。

## Configs 配置说明

日志记录器的配置在 [`LoggerConfig.DEFAULT_CONFIG`](middlewares/logs.py) 中定义，主要包括两个部分：

- **print**（控制台日志）：
  - `enabled`：是否启用控制台日志输出
  - `colored`：是否显示彩色样式
  - `log_level`：控制台日志的最低输出级别（如 `Levels.DEBUG`）
  - `time`：时间戳配置（格式、样式及模板）
  - `level`：各日志级别（DEBUG/INFO/NOTICE/WARNING/ERROR/CRITICAL）的显示文本及样式

- **file**（文件日志）：
  - `enabled`：是否启用文件日志输出
  - `colored`：是否在日志文件中包含 ANSI 转义码（一般应禁用）
  - `log_level`：文件日志输出的最低日志级别
  - `log_root_path`：日志文件存放的根目录
  - `log_name` 和 `log_suffix`：日志文件的前缀和后缀
  - `log_append_time`：是否在文件名中追加当前时间
  - `flush_every_n_logs`：日志缓冲区达到指定条数后自动刷新至文件
  - 同样包括 `time` 和 `level` 配置，用于控制时间戳与日志级别文本的样式

通过修改这些配置项，你可以灵活定制日志输出的路径、格式和样式。
