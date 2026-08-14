# deepseek-ai/deepseek-harness

> 2026-08-15 收录。DeepSeek 官方开源的 agent harness（`dsh`），"一切皆插件"架构，由 [Cordis](https://github.com/cordiverse/cordis) 驱动。目前处于**开发者预览**阶段，API 会快速迭代、有破坏性变更。

## 本地位置

- 源码：`D:\program\CC 工具库\tools\deepseek-harness`
- 版本：浅克隆 main（commit `47f9438`），已 `pnpm install` + `pnpm run build` 完整构建

## 这是什么

一个可自托管的 agent 智能体框架（类比 lm-evaluation-harness 之于评测，这是 agent 运行框架）：

- **一切皆插件**：插件、工具、能力缝（capability seam）都以插件形式组合
- 带 Web UI 图形界面 + headless 单任务模式 + CLI
- 包规模：`packages/` 下 40+ 个功能包（llm、mcp、sandbox、skill、workflow、subagent、terminal…），apps 下有 `cli` 与 `web`
- 自带中文文档（docs/ 大量 `.zh.md`），还带 Python SDK（`python/sdk-runtime`）

## 运行方式

### 已装好的源码方式（推荐）

```sh
cd "D:/program/CC 工具库/tools/deepseek-harness"
pnpm dsh web          # 启动 Web UI，默认 http://127.0.0.1:3080
pnpm dsh --profile headless "运行一次任务后退出"
```

前置：Node 18+（本机 v24.17.0）、pnpm（本机已装 11.7.0）。

### 免源码方式

```sh
npx @deepseek-ai/dsh web   # 走 npm registry，省去 clone/build
```

## 启动注意事项（踩坑记录）

- **首次启动很慢（可能 1 分钟+ 无输出）**：boot 时会执行 `healProfilesModuleFallback`，在 `~/.dsh/profiles/node_modules` 为整个依赖闭包逐个建 symlink（Windows 上尤其慢），**不是卡死**，耐心等。链接建好后冷启动首次 HTTP 请求约 16s，之后毫秒级。
- **首次打开需要配置 LLM API Key**：Web UI 会弹「添加一个 API Key 开始使用」，配置 provider 后才可用。
- 本机 7897 端口为代理，不影响本服务。

## 常用命令

| 命令 | 作用 |
|------|------|
| `pnpm dsh web` | 启动 Web UI（8080→3080 为 web 端口） |
| `pnpm dsh --profile headless "<任务>"` | 单任务 headless 模式 |
| `pnpm dsh --profile web --help` | 看 web app 自己的 flags |
| `pnpm dsh plugin --profile <name> add <包>` | 往 profile 装插件 |

## 注意

- 处于 **developer preview**：升级可能破坏兼容性，收藏的是固定 commit，更新前先看 release note
- 完整安装依赖用了 `--registry=https://registry.npmmirror.com`（国内镜像），约 2 分钟装完
- 两个 demo bin 的 `dsh-acp-demo` / `dsh-jsonrpc-agent` 在 pnpm install 时有 WARN（不影响主 CLI）
