# NoneBot 插件发布与商店上架规范研究

> 调研基准日与访问日期：2026-09-04（Asia/Shanghai）
> 范围：只采用 NoneBot 官方文档、`nonebot/nonebot2` 与 `nonebot/noneflow` 官方仓库源码。本文把官方用语中的“必须/禁止”和自动校验视为硬性要求，把“建议/推荐/强烈建议”单独标注。官方规则仍可能变化，正式提交前应再次核对链接内容。

## 一页结论

本项目若要重新发布，当前最直接的阻断项是：插件使用同步 `requests`（官方明确禁止阻塞事件循环）、没有可被 NoneFlow 读取的 `__plugin_meta__`、README 没有 NB-CLI 安装方式、直接向项目目录写 `./qqgroup` 而未使用 `nonebot-plugin-localstore`。旧式 `setup.py` 本身并非商店明文禁止，但官方当前推荐 `pyproject.toml`/PEP 621；采用 uv 是官方列出的模板路线之一。Ruff、pytest、特定覆盖率或特定目录布局不是商店自动检查的明文硬门槛，但应作为重构后的项目质量基线。

## 1. 发布标识与命名

| 项目 | 规则级别 | 当前规则 | 本项目应采用 |
| --- | --- | --- | --- |
| PyPI/仓库项目名 | 官方建议；提交表单必填 | 建议以 `nonebot-plugin-` 开头，单词用 `-` 分隔；必须是存在且可访问的 PyPI 项目名 | `nonebot-plugin-backup` |
| Python 模块名 | 官方建议；提交表单必填且自动校验 | 建议以 `nonebot_plugin_` 开头，单词用 `_` 分隔；必须是合法模块名 | `nonebot_plugin_backup` |
| 重复发布 | 自动校验 | PyPI 项目名与模块名的组合不可与商店现有记录重复（更新既有条目应走对应更新流程） | 发布前确认现有商店记录 |
| 展示名称 | 自动校验 | 来自插件元数据 `name`，最长 50 字符；这是人类可读名，不是模块索引名 | 例如“群文件备份” |

依据：[官方发布指南：命名与结构](https://nonebot.dev/docs/developer/plugin-publishing#%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C)、[官方发布 Issue 模板](https://github.com/nonebot/nonebot2/blob/master/.github/ISSUE_TEMPLATE/plugin_publish.yml)、[NoneFlow 校验模型](https://github.com/nonebot/noneflow/blob/main/src/providers/validation/models.py)、[NoneFlow 校验常量](https://github.com/nonebot/noneflow/blob/main/src/providers/validation/constants.py)（均访问于 2026-09-04）。

## 2. 包结构与构建发布

- 官方推荐（非强制）结构为顶层 `nonebot_plugin_backup/` 包，含 `__init__.py`（通常另有 `config.py`），仓库根目录放 `pyproject.toml` 与 `README.md`。
- 插件功能可以放在包的 `__init__.py`，也可拆分到子模块后由 `__init__.py` 导入；最外层插件模块必须实际可被 `nonebot.load_plugin("nonebot_plugin_backup")` 加载。
- 必须先把可安装发行包发布到 PyPI，商店表单会要求 PyPI 项目名；NoneFlow 会在隔离环境安装该项目并加载所填模块名。因此 wheel/sdist 必须包含全部运行代码与资源。
- 官方明确把 uv + `fllesser/nonebot-plugin-template` 列为三条模板路径之一，示例使用 `uv sync --all-groups -p 3.12`、`uv add`、`uv version --bump`；故本项目改为 uv/`pyproject.toml` 符合当前官方路线。
- 发布前官方建议实际构建并测试 wheel/sdist，避免代码或资源漏包。模板可由 `v*` tag 触发 GitHub Actions 发布；也可使用任何符合 PyPI/PEP 517 的构建发布方式。

依据：[官方发布指南：项目结构、uv 模板、构建和 PyPI 发布](https://nonebot.dev/docs/developer/plugin-publishing)（访问于 2026-09-04）。

## 3. 插件元数据（硬性）

插件最外层（通常 `nonebot_plugin_backup/__init__.py`）必须定义 `__plugin_meta__ = PluginMetadata(...)`。NoneFlow 会在加载后读取 `plugin.metadata`，缺失元数据直接判定失败。

| 字段 | 发布要求 |
| --- | --- |
| `name` | 必填，人类可读名称，自动校验最长 50 字符 |
| `description` | 必填，插件介绍；NoneFlow 输出中映射为 `desc` |
| `usage` | 必填，面向用户的用法 |
| `type` | 发布必填，只能是 `"application"`（直接提供机器人功能）或 `"library"`（供其他插件使用）；本项目应为 `application` |
| `homepage` | 发布必填，必须是 HTTP(S) URL且自动请求返回 200；通常填 GitHub 仓库 |
| `config` | 有配置类时必须填写，且该类必须是 Pydantic `BaseModel` 子类 |
| `supported_adapters` | 只使用 NoneBot 抽象时显式填 `None`；否则列出适配器，如 `{"~onebot.v11"}`。NoneFlow 会展开名称并核对适配器已存在于官方商店 |

若依赖其他插件提供的功能，必须先 `require("模块名")` 再 import。若支持的适配器受依赖插件限制，应在 `require()` 后使用 `inherit_supported_adapters()` 继承其范围。

依据：[官方发布指南：元数据与跨插件依赖](https://nonebot.dev/docs/developer/plugin-publishing#%E6%8F%92%E4%BB%B6%E5%85%83%E6%95%B0%E6%8D%AE)、[官方插件信息说明](https://nonebot.dev/docs/advanced/plugin-info)、[NoneFlow 加载 runner](https://github.com/nonebot/noneflow/blob/main/src/providers/docker_test/templates/runner.py.jinja)、[NoneFlow 校验模型](https://github.com/nonebot/noneflow/blob/main/src/providers/validation/models.py)（均访问于 2026-09-04）。

## 4. 依赖与异步规范

官方把下列内容置于“质量要求”，表述为“强烈建议完成，否则社区成员将要求修改”；其中同步阻塞与本地存储又明确使用“禁止/必须”，应按发布阻断项处理：

- 运行依赖必须包含 `nonebot2`，且包含代码直接使用的适配器（本项目为 `nonebot-adapter-onebot`）。
- 所有直接 import 的第三方包都必须在 `pyproject.toml` 的 `dependencies` 声明。
- 不得依赖 NoneBot V1 的 `nonebot` 包。
- 依赖不得用 `==` 锁死单一版本，使用 `>=` 或 `~=`；锁文件可固定开发环境，但发行依赖范围不应锁死。
- 禁止在插件事件循环中使用同步 HTTP（官方点名 `requests`）及其他长时间同步操作。应改用异步客户端；`aiohttp.ClientSession` 或官方示例中的 `httpx.AsyncClient` 均符合“异步且 await”的实质要求。
- 插件产生的数据、配置或缓存文件必须通过 `nonebot-plugin-localstore` 获取路径，不能写相对当前工作目录的 `./qqgroup`。依赖该插件时，代码需先 `require("nonebot_plugin_localstore")`。

依据：[官方发布指南：依赖、同步操作和本地存储](https://nonebot.dev/docs/developer/plugin-publishing#%E8%B4%A8%E9%87%8F%E8%A6%81%E6%B1%82)、[官方本地存储最佳实践](https://nonebot.dev/docs/best-practice/data-storing)（均访问于 2026-09-04）。

## 5. README/项目主页

README 至少应清楚覆盖：

- 插件功能介绍；
- 安装方法，**必须含 NB-CLI 安装命令**（本项目应写 `nb plugin install nonebot-plugin-backup`）；可再写 uv/pip 等方式；
- 不得指导用户使用旧式 `bot.py` 配置；
- 全部配置字段、默认值、类型/单位与示例（若有）；
- 触发命令/规则、权限与适配器限制；
- 其他操作说明；效果图按需添加。

此外应如实说明数据存放位置、下载/上传所需 OneBot API 与机器人权限、失败与覆盖行为。后半句是针对本项目的工程建议，不是商店 schema 字段。

依据：[官方发布指南：准备项目主页](https://nonebot.dev/docs/developer/plugin-publishing#%E5%87%86%E5%A4%87%E9%A1%B9%E7%9B%AE%E4%B8%BB%E9%A1%B5)、[官方商店安装说明](https://nonebot.dev/docs/tutorial/store)（均访问于 2026-09-04）。

## 6. 自动测试、格式与项目测试

### 商店硬性自动检查

NoneFlow 当前会在 Python 3.12 隔离环境中：安装 PyPI 项目、创建 fake driver 配置、写入提交表单中的 dotenv 配置、调用 `load_plugin(module_name)`、读取元数据，并验证：

- PyPI 项目存在、名称格式合法，模块名合法，二者组合不重复；
- 插件可成功安装并加载；
- 元数据存在且可序列化，`type` 合法，主页可访问；
- `config`（若给出）是 Pydantic `BaseModel` 子类；
- `supported_adapters` 格式正确且所列适配器存在于商店；
- 标签 JSON/JSON5 合法，最多 3 个，单个标签名最长 10 字符，颜色合法；
- 展示名最长 50 字符。

插件若无法零配置导入，必须在商店表单“插件配置项”提供测试用 dotenv；不得填 Token/API Key 等秘密。官方更推荐让插件零配置也能加载，只在实际使用相关功能时提示缺少配置。

### Ruff/pytest 的准确定位

当前发布指南、Issue 表单和 NoneFlow 校验源码没有规定必须使用 Ruff、pytest、特定覆盖率，也没有对提交插件仓库执行统一的 Ruff 格式检查。因此它们不是商店 schema 的硬性门槛。不过 Ruff + pytest 是本项目彻底重构后应有的维护基线：至少执行 `ruff check .`、`ruff format --check .`，并用测试覆盖配置解析、路径隔离、文件遍历/恢复逻辑、HTTP 下载错误与 NoneBot 插件加载。构建产物也应在干净环境安装后再跑加载测试。

依据：[NoneFlow 插件测试实现](https://github.com/nonebot/noneflow/blob/main/src/providers/docker_test/plugin_test.py)、[NoneFlow runner 模板](https://github.com/nonebot/noneflow/blob/main/src/providers/docker_test/templates/runner.py.jinja)、[NoneFlow 校验模型](https://github.com/nonebot/noneflow/blob/main/src/providers/validation/models.py)、[官方发布指南：基本要求](https://nonebot.dev/docs/developer/plugin-publishing#%E5%9F%BA%E6%9C%AC%E8%A6%81%E6%B1%82)（均访问于 2026-09-04）。

## 7. 商店提交流程

1. 完成重构、测试、版本更新，并构建 wheel/sdist。
2. 在干净环境验证 PyPI 将发布的产物可以安装并由模块名加载；先发布到 PyPI。
3. 打开 [NoneBot 插件商店](https://nonebot.dev/store/plugins)，点击“发布插件”，填写 PyPI 项目名、模块名、最多 3 个标签，以及必要的非敏感 dotenv 测试配置。
4. 表单会跳转到 `nonebot/nonebot2` 的“发布插件”Issue 页面；核对后提交。
5. 等待 NoneFlow 自动前置检查与维护者/志愿者人工代码审查。
6. 检查失败时不必关闭 Issue：修复插件、发布新的 PyPI 版本或修改信息后，勾选插件测试复选框重新触发。
7. 审核完成后，机器人创建的变更会自动合并进入商店。

依据：[官方发布指南：商店审核](https://nonebot.dev/docs/developer/plugin-publishing#%E5%95%86%E5%BA%97%E5%AE%A1%E6%A0%B8)、[官方发布 Issue 模板](https://github.com/nonebot/nonebot2/blob/master/.github/ISSUE_TEMPLATE/plugin_publish.yml)、[官方 NoneFlow 工作流](https://github.com/nonebot/nonebot2/blob/master/.github/workflows/noneflow.yml)（均访问于 2026-09-04）。

## 8. 本项目发布前检查表

- [ ] 用 `pyproject.toml`（PEP 621）取代旧 `setup.py`，使用 uv 生成/维护锁文件并验证构建。
- [ ] 保留规范发行名 `nonebot-plugin-backup` 与模块名 `nonebot_plugin_backup`。
- [ ] 在最外层加入完整 `PluginMetadata`，类型为 `application`，适配器为 `~onebot.v11`，配置类为 Pydantic 模型。
- [ ] 将 `requests` 和所有同步下载路径改成真正异步、流式写入的实现，避免把大文件一次性读入内存。
- [ ] 发行依赖列全：至少 `nonebot2`、`nonebot-adapter-onebot`、所选异步 HTTP 库、`nonebot-plugin-localstore`；不使用 `==`。
- [ ] 通过 localstore 获取数据目录，移除 `./qqgroup` 工作目录假设。
- [ ] 依赖插件全部先 `require()` 再 import。
- [ ] README 增加 NB-CLI 安装、配置表、权限/适配器、命令和数据目录说明，移除过时 go-cqhttp/旧版本信息。
- [ ] 用 Ruff 完成 lint/format，并建立 pytest 测试（项目质量基线，非商店硬校验）。
- [ ] 构建 sdist/wheel，在 Python 3.12 干净环境安装后验证 `load_plugin("nonebot_plugin_backup")` 和元数据。
- [ ] 发布 PyPI 新版本，再从商店表单提交或更新发布 Issue；不在测试配置中提交秘密。
