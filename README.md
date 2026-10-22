# OpenAI Official

[Sakura](https://github.com/Rvosy/Sakura) 的 ChatGPT 账号登录插件。登录后自动添加账号可用的 Codex 模型，用于对话、视觉对话和工具调用。使用账号的 Codex 额度，无需 API Key 或 Codex CLI。

## 运行要求

插件使用 Sakura Plugin API 4，依赖“OpenAI 兼容模型”基础插件和宿主的 Artifact、模型用途、设置服务。请保持基础插件启用，它提供模型服务工作台。

本插件还依赖尚未发布的 Sakura 配套改动：公共 SDK 的 `sakura_model_provider`、`sakura_openai_responses` 模块，以及模型服务贡献接口和 OpenAI 图标。使用前需准备包含这些改动的 Sakura 开发版本。

Python 依赖见 [requirements.txt](requirements.txt)，由 Sakura 安装：`openai==2.43.0`、`httpx[socks]==0.28.1`。

## 使用

1. 下载或克隆本仓库，在 Sakura 的“设置 → 插件”中从文件夹安装，启用并应用。
2. 打开“模型服务 → 添加模型服务”，选择“OpenAI Official”。每次选择都会新建一条连接，可在右侧修改名称。
3. 点击“登录 ChatGPT”，复制登录代码到浏览器打开的登录页。登录成功后自动获取并保存全部可用模型，同步失败可在账号面板重试。
4. 到“模型”页把对话模型换成 Codex 模型。视觉对话或其他插件用途也在此选择。

设备码登录需要在 ChatGPT 的安全设置或工作区权限中启用，见 [OpenAI 登录文档](https://developers.openai.com/codex/auth#preferred-device-code-authentication-beta)。登录代码按服务端返回的有效期等待，未指定时为 15 分钟。取消、切换服务、离开模型服务页或关闭设置会结束本次等待。

模型同步不会替换已选择的模型用途。温度、Top P、最大输出 Token 和 JSON 输出格式参数不发送给订阅接口；模型仍会收到完整的消息与工具定义。

## 账号与配置

每条连接分别保存 ChatGPT 账号和模型目录，可以同时配置多个账号。退出登录或删除一条连接不影响其他连接。退出登录会删除该连接的凭据，保留模型目录和用途；删除连接后，仍引用它的模型用途显示不可用，等待重新选择。

新连接的凭据保存在插件私有数据目录的 `accounts/<profileId>.json`。已有单账号连接保留原来的 `auth.json` 和模型引用。不读取或改写 Codex CLI 的登录文件。

访问令牌到期时自动续期；有效期未知时先使用现有令牌。服务返回 401 时，续期后重试一次；网络中断、额度不足或服务故障不会自动重发生成请求。

[config.json](config.json) 中的 `timeout_seconds` 是请求超时秒数，默认 120。账号和同步的模型由插件保存，无需手动配置。

登录连接 `auth.openai.com`，模型目录和请求连接 `chatgpt.com/backend-api/codex`，沿用 Sakura 的系统代理。403 时检查账号和模型权限，429 时检查订阅额度；登录过期且续期失败时重新登录。

## 开发与测试

插件负责账号、模型目录、订阅地址和参数差异。公共 SDK 的 `ModelProvider` 负责调用者隔离、任务、取消与 Artifact 交付，`sakura_openai_responses` 负责消息转换和流式结果；HTTP 与 SSE 解码使用 OpenAI SDK。主程序和其他插件继续使用公共 `ModelClient`。

测试复用 Sakura 的开发环境和公共 SDK，在本仓库根目录运行：

```powershell
$env:SAKURA_SOURCE = 'D:\Project\sakura'
& "$env:SAKURA_SOURCE\runtime\python.exe" -m pytest -q tests
```

macOS / Linux 使用 `SAKURA_SOURCE=/path/to/sakura /path/to/sakura/runtime/bin/python -m pytest -q tests`。测试覆盖设备码登录、令牌续期、多账号隔离、自动同步、取消重试和流式响应，使用模拟 HTTP，不连接真实账号。

## 许可证与参考

代码使用 [MIT 许可证](LICENSE)。OpenAI 图标由 Sakura 宿主提供，本仓库不包含图标资源。

实现参考 [MaiBot Codex 订阅插件](https://github.com/ChenXi2542/maibot-codex-subscription)、[OpenCode](https://github.com/anomalyco/opencode) 和 [pi](https://github.com/earendil-works/pi)。名称和登录交互参考 [cc-switch](https://github.com/farion1231/cc-switch)。
