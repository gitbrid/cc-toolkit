def recommend(project):
    text = (
        f"{project.get('name', '')} {project.get('description', '')} "
        f"{' '.join(project.get('topics', []))}"
    ).lower()
    reasons = []
    if any(k in text for k in ("llm", "ai", "agent", "chatgpt", "deepseek", "rag")):
        reasons.append("AI/LLM 方向，可能对你的 Agent 工具链有直接参考价值")
    if project.get("language") == "Python" or "python" in text:
        reasons.append("Python 技术栈，适合做脚本、自动化或工具扩展")
    if any(k in text for k in ("obsidian", "note", "knowledge", "markdown")):
        reasons.append("与 Obsidian/笔记/知识管理相关，可直接借鉴或集成")
    if any(k in text for k in ("mcp", "model context protocol")):
        reasons.append("MCP 生态项目，可对照你的 MCP 收藏库评估")
    if any(k in text for k in ("automation", "workflow", "cli", "crawler", "scrape")):
        reasons.append("偏自动化和工程效率，适合补进工具库场景")
    if not reasons:
        reasons.append("值得关注的新项目，建议按文档判断是否适合你的工作流")
    return "；".join(reasons) + "。"
