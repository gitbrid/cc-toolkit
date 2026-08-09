# leoyang1984/obsidian-deepseek-note-helper

> 2026-08-09 收录。Obsidian 侧边栏 DeepSeek 助手插件：读当前笔记、穿透双向链接、全库 RAG 检索、自动维护 YAML 元数据。

## 本地位置

- 源码：`D:\program\CC 工具库\plugins\obsidian-deepseek-note-helper`
- 版本：1.0.0（main）

## 能力

- 当前笔记全文作为上下文，高亮选区自动聚焦
- 自动解析 `[[双向链接]]` 并带入关联笔记内容
- DeepSeek Function Calling：`search_vault`、`create_note`、`append_to_note`、`update_metadata`
- 10 轮上下文记忆，原生 Markdown 渲染
- 支持自定义 API URL / Model，可走中转或 new-api

## 构建

```powershell
cd D:\program\CC 工具库\plugins\obsidian-deepseek-note-helper
npm install
node esbuild.config.js production
```

构建产物为插件根目录 `main.js`，配合 `manifest.json`、`styles.css` 即可安装。

## 安装到 Obsidian

把三个文件放进 vault 的 `.obsidian/plugins/deepseek-note-helper/`，重启 Obsidian 后启用，再在插件设置里填 DeepSeek API Key / Base URL / Model。

## 当前状态（2026-08-09）

- 已安装到 `D:\program\Codex\Codex`、`D:\Obsidian\b站视频文稿`、`D:\Albert's vault`
- 已写入 `.obsidian/community-plugins.json` 启用列表
- 已写入插件 `data.json`：API URL `https://api.deepseek.com`，模型 `deepseek-v4-flash`
- 需要在 Obsidian 中重启/重载 vault；若之前开启受限模式，先关闭后再启用插件

## 注意

- 插件有改笔记权限，先在小 vault 或测试笔记上试用
- API Key 由 Obsidian 插件设置保管，不写入工具库
- 如果走 new-api，Base URL 填 `http://localhost:3000`，模型填 `deepseek-v4-flash`
