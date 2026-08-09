import { mkdir, readFile, writeFile, appendFile } from "node:fs/promises";
import { execFile, execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import OpenAI from "openai";
import { z } from "zod";

const execFileAsync = promisify(execFile);

function readLaunchctlEnv(name) {
  if (process.platform !== "darwin") return "";
  try {
    return execFileSync("launchctl", ["getenv", name], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return "";
  }
}

const apiKey = process.env.DEEPSEEK_API_KEY || readLaunchctlEnv("DEEPSEEK_API_KEY");
const configuredModel =
  process.env.DEEPSEEKHELPER_MODEL || process.env.DEEPSEEK_MODEL || "auto";
const baseURL = process.env.DEEPSEEK_BASE_URL || "https://api.deepseek.com";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const pluginDir = path.resolve(scriptDir, "..");
const dataDir = process.env.DEEPSEEKHELPER_DATA_DIR || path.join(pluginDir, "data");
const usageLogPath =
  process.env.DEEPSEEKHELPER_USAGE_LOG || path.join(dataDir, "usage.jsonl");
const modelCachePath =
  process.env.DEEPSEEKHELPER_MODEL_CACHE || path.join(dataDir, "models-cache.json");

const KNOWN_MODELS = ["deepseek-v4-flash", "deepseek-v4-pro"];
const requestedModelCacheDays = Number(process.env.DEEPSEEKHELPER_MODEL_CACHE_DAYS || 1);
const MODEL_CACHE_TTL_DAYS =
  Number.isFinite(requestedModelCacheDays) && requestedModelCacheDays > 0
    ? requestedModelCacheDays
    : 1;
const MODEL_CACHE_TTL_MS = MODEL_CACHE_TTL_DAYS * 24 * 60 * 60 * 1000;

const MODEL_PROFILES = {
  flash: {
    label: "flash",
    characteristics: "fast, cost-efficient, suitable for supervised low and medium complexity work",
    defaultThinking: "disabled",
    defaultReasoningEffort: null,
    bestFor: ["low/medium code suggestions", "documentation drafts", "summaries", "prompt drafting"],
    pricingUSDPerMTok: {
      inputCacheHit: 0.0028,
      inputCacheMiss: 0.14,
      output: 0.28,
    },
  },
  pro: {
    label: "pro",
    characteristics: "stronger reasoning, suitable for review, verification, and higher-risk decisions",
    defaultThinking: "enabled",
    defaultReasoningEffort: "high",
    bestFor: ["code review", "architecture discussion", "risk analysis", "verification"],
    pricingUSDPerMTok: {
      inputCacheHit: 0.003625,
      inputCacheMiss: 0.435,
      output: 0.87,
    },
  },
};

let modelCache = null;

if (!apiKey) {
  console.error("DEEPSEEK_API_KEY is required to run the deepseekhelper MCP server.");
  process.exit(1);
}

const client = new OpenAI({
  apiKey,
  baseURL,
});

const server = new McpServer({
  name: "deepseekhelper",
  version: "0.3.4",
});

function sanitizeErrorMessage(error) {
  const raw = error instanceof Error ? error.message : String(error);
  return raw
    .replace(/sk-[A-Za-z0-9_-]+/g, "sk-***")
    .replace(/Bearer\s+[A-Za-z0-9._-]+/gi, "Bearer ***")
    .replace(/api key:\s*[^,\n]+/gi, "api key: ***");
}

async function ensureDataDir() {
  await mkdir(dataDir, { recursive: true });
}

async function readJsonFile(filePath) {
  try {
    return JSON.parse(await readFile(filePath, "utf8"));
  } catch {
    return null;
  }
}

async function writeJsonFile(filePath, value) {
  await ensureDataDir();
  await writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function runCommand(command, args, options = {}) {
  try {
    const result = await execFileAsync(command, args, {
      cwd: pluginDir,
      timeout: options.timeout || 60_000,
      maxBuffer: options.maxBuffer || 1024 * 1024,
      env: process.env,
    });
    return {
      ok: true,
      stdout: result.stdout.trim(),
      stderr: result.stderr.trim(),
    };
  } catch (error) {
    return {
      ok: false,
      stdout: error.stdout?.trim?.() || "",
      stderr: error.stderr?.trim?.() || "",
      error: sanitizeErrorMessage(error),
      code: error.code ?? null,
    };
  }
}

async function git(args, options = {}) {
  return runCommand("git", args, options);
}

async function npm(args, options = {}) {
  return runCommand("npm", args, { timeout: 180_000, ...options });
}

function commandOutput(result) {
  return [result.stdout, result.stderr, result.error].filter(Boolean).join("\n").trim();
}

async function getPackageVersion() {
  const pkg = await readJsonFile(path.join(pluginDir, "package.json"));
  return pkg?.version || "unknown";
}

async function currentHead() {
  const result = await git(["rev-parse", "--short", "HEAD"]);
  return result.ok ? result.stdout : "unknown";
}

async function currentBranch() {
  const result = await git(["branch", "--show-current"]);
  return result.ok ? result.stdout : "unknown";
}

async function upstreamRef() {
  const result = await git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"]);
  return result.ok ? result.stdout : null;
}

async function workingTreeStatus() {
  const result = await git(["status", "--porcelain"]);
  if (!result.ok) {
    return {
      clean: false,
      status: commandOutput(result) || "Unable to read git status.",
    };
  }
  return {
    clean: result.stdout.length === 0,
    status: result.stdout,
  };
}

async function gitFileSha(ref, filePath) {
  const result = await git(["rev-parse", `${ref}:${filePath}`]);
  return result.ok ? result.stdout : null;
}

async function updateSnapshot() {
  const [version, head, branch, upstream, tree] = await Promise.all([
    getPackageVersion(),
    currentHead(),
    currentBranch(),
    upstreamRef(),
    workingTreeStatus(),
  ]);

  return {
    version,
    head,
    branch,
    upstream,
    clean: tree.clean,
    status: tree.status,
  };
}

function isFreshCache(cache, now = Date.now()) {
  return cache?.fetchedAt && now - cache.fetchedAt < MODEL_CACHE_TTL_MS;
}

function modelVersion(model) {
  const match = model.match(/deepseek-v(\d+(?:\.\d+)?)/i);
  return match ? Number(match[1]) : 0;
}

function modelTier(model) {
  if (model.includes("-flash")) return "flash";
  if (model.includes("-pro")) return "pro";
  if (model === "deepseek-chat") return "flash";
  if (model === "deepseek-reasoner") return "flash";
  return "unknown";
}

function modelProfile(model) {
  return MODEL_PROFILES[modelTier(model)] || {
    label: "unknown",
    characteristics: "unknown DeepSeek model tier",
    defaultThinking: "enabled",
    defaultReasoningEffort: "high",
    bestFor: ["explicit user-selected model"],
    pricingUSDPerMTok: null,
  };
}

function latestModelForTier(models, tier) {
  const candidates = models
    .filter((model) => model.includes(`-${tier}`))
    .filter((model) => !["deepseek-chat", "deepseek-reasoner"].includes(model));

  candidates.sort((a, b) => {
    const versionDelta = modelVersion(b) - modelVersion(a);
    return versionDelta || a.localeCompare(b);
  });

  return candidates[0] || null;
}

function automaticModelFor(purpose, difficulty = "medium", models = KNOWN_MODELS) {
  const tier =
    purpose === "task" && difficulty !== "high"
      ? "flash"
      : purpose === "prompt"
        ? "flash"
        : "pro";
  const fallback = tier === "flash" ? "deepseek-v4-flash" : "deepseek-v4-pro";
  return latestModelForTier(models, tier) || fallback;
}

function resolveModel({ requestedModel, purpose, difficulty, availableModels }) {
  if (requestedModel) {
    return {
      model: requestedModel,
      source: "explicit tool argument",
    };
  }

  if (configuredModel && configuredModel !== "auto") {
    return {
      model: configuredModel,
      source: "DEEPSEEKHELPER_MODEL/DEEPSEEK_MODEL",
    };
  }

  const model = automaticModelFor(purpose, difficulty, availableModels);
  return {
    model,
    source: `automatic latest-${model.includes("-flash") ? "flash" : "pro"} ${purpose}${
      difficulty ? `/${difficulty}` : ""
    } policy`,
  };
}

function resolveThinking({ model, purpose, requestedThinking, requestedReasoningEffort }) {
  const profile = modelProfile(model);
  const thinking =
    requestedThinking && requestedThinking !== "auto"
      ? requestedThinking
      : profile.defaultThinking;

  const reasoningEffort =
    thinking === "enabled"
      ? requestedReasoningEffort || profile.defaultReasoningEffort || "high"
      : null;

  return {
    thinking,
    reasoningEffort,
    source:
      requestedThinking && requestedThinking !== "auto"
        ? "explicit tool argument"
        : `${profile.label} ${purpose} profile`,
    profile,
  };
}

async function listModels({ refresh = false } = {}) {
  const now = Date.now();
  if (!refresh && isFreshCache(modelCache, now)) {
    return modelCache;
  }

  if (!refresh) {
    const persisted = await readJsonFile(modelCachePath);
    if (isFreshCache(persisted, now)) {
      modelCache = persisted;
      return modelCache;
    }
  }

  try {
    const response = await fetch(`${baseURL}/models`, {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} ${response.statusText}`);
    }

    const body = await response.json();
    const models = Array.isArray(body.data)
      ? body.data.map((model) => model.id).filter(Boolean)
      : [];

    modelCache = {
      models,
      source: `${baseURL}/models`,
      fetchedAt: now,
      ttlDays: MODEL_CACHE_TTL_DAYS,
      error: null,
    };
    await writeJsonFile(modelCachePath, modelCache);
    return modelCache;
  } catch (error) {
    const persisted = await readJsonFile(modelCachePath);
    if (persisted?.models?.length) {
      modelCache = {
        ...persisted,
        source: `${persisted.source || "persisted cache"} (stale fallback)`,
        error: error instanceof Error ? error.message : String(error),
      };
      return modelCache;
    }

    modelCache = {
      models: KNOWN_MODELS,
      source: "built-in fallback",
      fetchedAt: now,
      ttlDays: MODEL_CACHE_TTL_DAYS,
      error: error instanceof Error ? error.message : String(error),
    };
    return modelCache;
  }
}

async function ensureModel(model, available) {
  if (!available.models.includes(model)) {
    throw new Error(
      `Model "${model}" is not in the available model list (${available.models.join(
        ", "
      )}). Model list source: ${available.source}${
        available.error ? `; list warning: ${available.error}` : ""
      }`
    );
  }
}

function normalizeUsage(usage) {
  const promptTokens = usage?.prompt_tokens ?? 0;
  const completionTokens = usage?.completion_tokens ?? 0;
  const totalTokens = usage?.total_tokens ?? promptTokens + completionTokens;
  const promptCacheHitTokens = usage?.prompt_cache_hit_tokens ?? 0;
  const promptCacheMissTokens =
    usage?.prompt_cache_miss_tokens ?? Math.max(promptTokens - promptCacheHitTokens, 0);

  return {
    prompt_tokens: promptTokens,
    completion_tokens: completionTokens,
    total_tokens: totalTokens,
    prompt_cache_hit_tokens: promptCacheHitTokens,
    prompt_cache_miss_tokens: promptCacheMissTokens,
  };
}

function estimateCostUSD(model, usage) {
  const prices = modelProfile(model).pricingUSDPerMTok;
  if (!prices) return null;

  const cost =
    (usage.prompt_cache_hit_tokens / 1_000_000) * prices.inputCacheHit +
    (usage.prompt_cache_miss_tokens / 1_000_000) * prices.inputCacheMiss +
    (usage.completion_tokens / 1_000_000) * prices.output;

  return Number(cost.toFixed(8));
}

async function recordUsage(entry) {
  await ensureDataDir();
  await appendFile(usageLogPath, `${JSON.stringify(entry)}\n`, "utf8");
}

async function chat({
  tool,
  purpose,
  difficulty,
  requestedModel,
  requestedThinking,
  requestedReasoningEffort,
  system,
  user,
}) {
  const available = await listModels();
  const selection = resolveModel({
    requestedModel,
    purpose,
    difficulty,
    availableModels: available.models,
  });
  await ensureModel(selection.model, available);

  const thinking = resolveThinking({
    model: selection.model,
    purpose,
    requestedThinking,
    requestedReasoningEffort,
  });

  const request = {
    model: selection.model,
    messages: [
      {
        role: "system",
        content: system,
      },
      {
        role: "user",
        content: user,
      },
    ],
    extra_body: {
      thinking: {
        type: thinking.thinking,
      },
    },
  };

  if (thinking.thinking === "enabled" && thinking.reasoningEffort) {
    request.reasoning_effort = thinking.reasoningEffort;
  }

  let response;
  try {
    response = await client.chat.completions.create(request);
  } catch (error) {
    throw new Error(`DeepSeek chat completion failed: ${sanitizeErrorMessage(error)}`);
  }
  const usage = normalizeUsage(response.usage);
  const estimatedCostUSD = estimateCostUSD(selection.model, usage);
  const ts = new Date().toISOString();

  await recordUsage({
    ts,
    tool,
    purpose,
    difficulty: difficulty || null,
    model: selection.model,
    model_tier: modelTier(selection.model),
    model_selection: selection.source,
    thinking: thinking.thinking,
    reasoning_effort: thinking.reasoningEffort,
    thinking_selection: thinking.source,
    ...usage,
    estimated_cost_usd: estimatedCostUSD,
  });

  return {
    model: selection.model,
    modelSource: selection.source,
    modelProfile: thinking.profile,
    thinking: thinking.thinking,
    reasoningEffort: thinking.reasoningEffort,
    thinkingSource: thinking.source,
    usage,
    estimatedCostUSD,
    text: response.choices[0]?.message?.content || "DeepSeek returned no text.",
  };
}

function formatCost(cost) {
  return cost == null ? "n/a" : `$${cost.toFixed(6)}`;
}

function textResult(title, result) {
  const usage = result.usage
    ? [
        `Tokens: prompt ${result.usage.prompt_tokens}, completion ${result.usage.completion_tokens}, total ${result.usage.total_tokens}`,
        `Cache: hit ${result.usage.prompt_cache_hit_tokens}, miss ${result.usage.prompt_cache_miss_tokens}`,
        `Estimated cost: ${formatCost(result.estimatedCostUSD)}`,
      ].join("\n")
    : "";

  return {
    content: [
      {
        type: "text",
        text: `${title}\nModel: ${result.model}\nSelection: ${result.modelSource}\nModel profile: ${result.modelProfile.characteristics}\nThinking: ${result.thinking}${
          result.reasoningEffort ? ` (${result.reasoningEffort})` : ""
        }\nThinking selection: ${result.thinkingSource}\n${usage}\n\n${result.text}`,
      },
    ],
  };
}

function joinSections(sections) {
  return sections.filter(Boolean).join("\n\n");
}

async function readUsageEntries() {
  try {
    const raw = await readFile(usageLogPath, "utf8");
    return raw
      .split("\n")
      .filter(Boolean)
      .map((line) => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      })
      .filter(Boolean);
  } catch {
    return [];
  }
}

function periodStart(period) {
  const now = new Date();
  if (period === "all") return null;
  if (period === "today") {
    return new Date(now.getFullYear(), now.getMonth(), now.getDate());
  }
  const days = period === "7d" ? 7 : 30;
  return new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
}

function aggregate(entries) {
  const totals = {
    calls: 0,
    prompt_tokens: 0,
    completion_tokens: 0,
    total_tokens: 0,
    prompt_cache_hit_tokens: 0,
    prompt_cache_miss_tokens: 0,
    estimated_cost_usd: 0,
  };
  const byModel = new Map();
  const byTool = new Map();

  for (const entry of entries) {
    totals.calls += 1;
    for (const key of [
      "prompt_tokens",
      "completion_tokens",
      "total_tokens",
      "prompt_cache_hit_tokens",
      "prompt_cache_miss_tokens",
      "estimated_cost_usd",
    ]) {
      totals[key] += Number(entry[key] || 0);
    }

    for (const [map, key] of [
      [byModel, entry.model || "unknown"],
      [byTool, entry.tool || "unknown"],
    ]) {
      const current = map.get(key) || { calls: 0, total_tokens: 0, estimated_cost_usd: 0 };
      current.calls += 1;
      current.total_tokens += Number(entry.total_tokens || 0);
      current.estimated_cost_usd += Number(entry.estimated_cost_usd || 0);
      map.set(key, current);
    }
  }

  return { totals, byModel, byTool };
}

function formatBreakdown(title, map) {
  if (!map.size) return `${title}: none`;
  const lines = [`${title}:`];
  for (const [name, value] of [...map.entries()].sort((a, b) => b[1].total_tokens - a[1].total_tokens)) {
    lines.push(
      `- ${name}: ${value.calls} calls, ${value.total_tokens} tokens, ${formatCost(
        value.estimated_cost_usd
      )}`
    );
  }
  return lines.join("\n");
}

const modelArg = z
  .string()
  .optional()
  .describe("Optional DeepSeek model id. Overrides configured and automatic model selection.");

const thinkingArg = z
  .enum(["auto", "enabled", "disabled"])
  .optional()
  .describe("Thinking mode. auto uses the selected model profile.");

const reasoningEffortArg = z
  .enum(["high", "max"])
  .optional()
  .describe("Reasoning effort when thinking mode is enabled.");

server.tool(
  "deepseekhelper_status",
  "Show DeepSeekHelper configuration, default model policy, data paths, and optionally refresh available models.",
  {
    refresh_models: z.boolean().optional().describe("Set true to refresh DeepSeek's /models list."),
  },
  async ({ refresh_models }) => {
    const models = await listModels({ refresh: Boolean(refresh_models) });
    const autoTaskModel = automaticModelFor("task", "medium", models.models);
    const autoPromptModel = automaticModelFor("prompt", "medium", models.models);
    const autoReviewModel = automaticModelFor("review", "high", models.models);
    const lines = [
      "DeepSeekHelper status",
      `Base URL: ${baseURL}`,
      `Configured model: ${configuredModel}`,
      `Model cache TTL: ${MODEL_CACHE_TTL_DAYS} day(s)`,
      `Model cache path: ${modelCachePath}`,
      `Usage log path: ${usageLogPath}`,
      "Automatic policy:",
      `- deepseek_task low/medium: latest flash-class model (${autoTaskModel}), thinking ${MODEL_PROFILES.flash.defaultThinking}`,
      `- deepseek_prompt: latest flash-class model (${autoPromptModel}), thinking ${MODEL_PROFILES.flash.defaultThinking}`,
      `- deepseek_review/deepseek_discuss/deepseek_verify/high-complexity support: latest pro-class model (${autoReviewModel}), thinking ${MODEL_PROFILES.pro.defaultThinking}/${MODEL_PROFILES.pro.defaultReasoningEffort}`,
      `Available models (${models.source}): ${models.models.join(", ") || "(none)"}`,
    ];

    if (models.error) {
      lines.push(`Model list warning: ${models.error}`);
    }

    return {
      content: [
        {
          type: "text",
          text: lines.join("\n"),
        },
      ],
    };
  }
);

server.tool(
  "deepseek_models",
  "Fetch the currently available DeepSeek API models and show DeepSeekHelper's profile classification.",
  {
    refresh: z.boolean().optional().describe("Set true to bypass the daily local model cache."),
  },
  async ({ refresh }) => {
    const models = await listModels({ refresh: Boolean(refresh) });
    const profileLines = models.models.map((model) => {
      const profile = modelProfile(model);
      return `- ${model}: ${profile.label}; ${profile.characteristics}`;
    });

    return {
      content: [
        {
          type: "text",
          text: joinSections([
            `Available models: ${models.models.join(", ") || "(none)"}`,
            `Source: ${models.source}`,
            `Cache TTL: ${MODEL_CACHE_TTL_DAYS} day(s)`,
            profileLines.length ? profileLines.join("\n") : null,
            models.error ? `Warning: ${models.error}` : null,
          ]),
        },
      ],
    };
  }
);

server.tool(
  "deepseek_auth_check",
  "Verify that the configured DeepSeek API key can call both /models and chat completions.",
  {},
  async () => {
    const models = await listModels({ refresh: true });
    const model = automaticModelFor("prompt", "low", models.models);

    try {
      const response = await client.chat.completions.create({
        model,
        messages: [
          {
            role: "system",
            content: "Reply with exactly: ok",
          },
          {
            role: "user",
            content: "health check",
          },
        ],
        extra_body: {
          thinking: {
            type: "disabled",
          },
        },
      });

      const usage = normalizeUsage(response.usage);
      return {
        content: [
          {
            type: "text",
            text: [
              "DeepSeek auth check: ok",
              `Models endpoint: ok (${models.models.join(", ")})`,
              `Chat completion endpoint: ok (${model})`,
              `Tokens: prompt ${usage.prompt_tokens}, completion ${usage.completion_tokens}, total ${usage.total_tokens}`,
            ].join("\n"),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: [
              "DeepSeek auth check: failed",
              `Models endpoint: ${models.error ? `warning (${models.error})` : "ok"}`,
              `Chat completion endpoint: failed (${sanitizeErrorMessage(error)})`,
              "Likely causes: invalid API key, wrong account/project, expired/revoked key, insufficient account balance, or an environment value different from the intended key.",
            ].join("\n"),
          },
        ],
      };
    }
  }
);

server.tool(
  "deepseek_usage_summary",
  "Summarize DeepSeekHelper token usage, cache hits, and estimated cost.",
  {
    period: z
      .enum(["today", "7d", "30d", "all"])
      .optional()
      .describe("Usage period to summarize."),
  },
  async ({ period }) => {
    const selectedPeriod = period || "today";
    const start = periodStart(selectedPeriod);
    const entries = (await readUsageEntries()).filter((entry) => {
      if (!start) return true;
      return new Date(entry.ts) >= start;
    });
    const { totals, byModel, byTool } = aggregate(entries);
    const cacheDenominator =
      totals.prompt_cache_hit_tokens + totals.prompt_cache_miss_tokens;
    const cacheRate = cacheDenominator
      ? ((totals.prompt_cache_hit_tokens / cacheDenominator) * 100).toFixed(2)
      : "0.00";

    return {
      content: [
        {
          type: "text",
          text: joinSections([
            `DeepSeekHelper usage summary\nPeriod: ${selectedPeriod}\nLog: ${usageLogPath}`,
            `Calls: ${totals.calls}`,
            `Tokens: prompt ${totals.prompt_tokens}, completion ${totals.completion_tokens}, total ${totals.total_tokens}`,
            `Cache: hit ${totals.prompt_cache_hit_tokens}, miss ${totals.prompt_cache_miss_tokens}, hit rate ${cacheRate}%`,
            `Estimated cost: ${formatCost(totals.estimated_cost_usd)}`,
            formatBreakdown("By model", byModel),
            formatBreakdown("By tool", byTool),
          ]),
        },
      ],
    };
  }
);

server.tool(
  "deepseek_usage_tail",
  "Show recent DeepSeekHelper usage records without prompt or response content.",
  {
    limit: z.number().int().min(1).max(100).optional().describe("Number of records to return."),
  },
  async ({ limit }) => {
    const records = (await readUsageEntries()).slice(-(limit || 10));
    const lines = records.map((entry) =>
      [
        entry.ts,
        entry.tool,
        entry.model,
        `thinking=${entry.thinking}${entry.reasoning_effort ? `/${entry.reasoning_effort}` : ""}`,
        `tokens=${entry.total_tokens}`,
        `cache_hit=${entry.prompt_cache_hit_tokens}`,
        `cache_miss=${entry.prompt_cache_miss_tokens}`,
        `cost=${formatCost(Number(entry.estimated_cost_usd || 0))}`,
      ].join(" | ")
    );

    return {
      content: [
        {
          type: "text",
          text: lines.length ? lines.join("\n") : `No usage records found at ${usageLogPath}.`,
        },
      ],
    };
  }
);

server.tool(
  "deepseek_update_check",
  "Check whether DeepSeekHelper can be updated from its git upstream without modifying files.",
  {
    fetch: z
      .boolean()
      .optional()
      .describe("Set true to fetch the upstream before comparing. This performs network I/O but does not modify files."),
  },
  async ({ fetch }) => {
    const before = await updateSnapshot();
    const lines = [
      "DeepSeekHelper update check",
      `Plugin directory: ${pluginDir}`,
      `Version: ${before.version}`,
      `Branch: ${before.branch}`,
      `HEAD: ${before.head}`,
      `Upstream: ${before.upstream || "(none)"}`,
      `Working tree: ${before.clean ? "clean" : "dirty"}`,
    ];

    if (!before.upstream) {
      lines.push("Update status: unavailable because no git upstream is configured.");
      return { content: [{ type: "text", text: lines.join("\n") }] };
    }

    if (!before.clean) {
      lines.push("Local changes:");
      lines.push(before.status);
      lines.push("Update status: blocked until local changes are committed, stashed, or discarded by the user.");
      return { content: [{ type: "text", text: lines.join("\n") }] };
    }

    if (fetch) {
      const fetchResult = await git(["fetch", "--prune"]);
      if (!fetchResult.ok) {
        lines.push(`Fetch: failed\n${commandOutput(fetchResult)}`);
        return { content: [{ type: "text", text: lines.join("\n") }] };
      }
      lines.push("Fetch: ok");
    } else {
      lines.push("Fetch: skipped; pass fetch=true to refresh remote state.");
    }

    const aheadBehind = await git(["rev-list", "--left-right", "--count", "HEAD...@{u}"]);
    if (!aheadBehind.ok) {
      lines.push(`Compare: failed\n${commandOutput(aheadBehind)}`);
      return { content: [{ type: "text", text: lines.join("\n") }] };
    }

    const [ahead, behind] = aheadBehind.stdout.split(/\s+/).map((value) => Number(value || 0));
    lines.push(`Ahead: ${ahead}`);
    lines.push(`Behind: ${behind}`);
    lines.push(
      behind > 0
        ? "Update status: update available. Call deepseek_update_apply to fast-forward."
        : "Update status: already up to date."
    );

    return { content: [{ type: "text", text: lines.join("\n") }] };
  }
);

server.tool(
  "deepseek_update_apply",
  "Update DeepSeekHelper from its git upstream with a fast-forward pull. This only runs when explicitly called.",
  {
    install_dependencies: z
      .boolean()
      .optional()
      .describe("Set true to run npm install if package.json or package-lock.json changed."),
  },
  async ({ install_dependencies }) => {
    const before = await updateSnapshot();
    const lines = [
      "DeepSeekHelper update apply",
      `Plugin directory: ${pluginDir}`,
      `Starting version: ${before.version}`,
      `Starting HEAD: ${before.head}`,
      `Branch: ${before.branch}`,
      `Upstream: ${before.upstream || "(none)"}`,
    ];

    if (!before.upstream) {
      lines.push("Update refused: no git upstream is configured.");
      return { content: [{ type: "text", text: lines.join("\n") }] };
    }

    if (!before.clean) {
      lines.push("Update refused: working tree has local changes.");
      lines.push(before.status);
      return { content: [{ type: "text", text: lines.join("\n") }] };
    }

    const beforePackageSha = await gitFileSha("HEAD", "package.json");
    const beforeLockSha = await gitFileSha("HEAD", "package-lock.json");

    const fetchResult = await git(["fetch", "--prune"]);
    if (!fetchResult.ok) {
      lines.push(`Fetch failed:\n${commandOutput(fetchResult)}`);
      return { content: [{ type: "text", text: lines.join("\n") }] };
    }
    lines.push("Fetch: ok");

    const pullResult = await git(["pull", "--ff-only"]);
    if (!pullResult.ok) {
      lines.push(`Pull failed:\n${commandOutput(pullResult)}`);
      return { content: [{ type: "text", text: lines.join("\n") }] };
    }
    lines.push(`Pull: ok${pullResult.stdout ? `\n${pullResult.stdout}` : ""}`);

    const after = await updateSnapshot();
    const afterPackageSha = await gitFileSha("HEAD", "package.json");
    const afterLockSha = await gitFileSha("HEAD", "package-lock.json");
    const dependencyFilesChanged =
      beforePackageSha !== afterPackageSha || beforeLockSha !== afterLockSha;

    lines.push(`Updated version: ${after.version}`);
    lines.push(`Updated HEAD: ${after.head}`);
    lines.push(`Dependency files changed: ${dependencyFilesChanged ? "yes" : "no"}`);

    if (dependencyFilesChanged) {
      if (install_dependencies) {
        const installResult = await npm(["install"]);
        if (!installResult.ok) {
          lines.push(`npm install failed:\n${commandOutput(installResult)}`);
          lines.push("Codex should not use the updated plugin until dependencies are fixed.");
          return { content: [{ type: "text", text: lines.join("\n") }] };
        }
        lines.push("npm install: ok");
      } else {
        lines.push("npm install: skipped; call again with install_dependencies=true if dependency files changed.");
      }
    }

    lines.push("Reload or restart Codex so the MCP server uses the updated plugin code.");
    return { content: [{ type: "text", text: lines.join("\n") }] };
  }
);

server.tool(
  "deepseek_task",
  "Ask DeepSeek to handle a low or medium difficulty coding, documentation, or design task under Codex supervision.",
  {
    task: z.string().min(1).describe("The task DeepSeek should work on."),
    context: z.string().optional().describe("Relevant code, docs, requirements, logs, or constraints."),
    difficulty: z
      .enum(["low", "medium"])
      .optional()
      .describe("Only low and medium difficulty tasks are accepted for delegated execution."),
    output_type: z
      .enum(["implementation_plan", "unified_diff", "code_snippet", "doc_draft", "design_draft"])
      .optional()
      .describe("Preferred output format."),
    constraints: z.string().optional().describe("Rules DeepSeek must follow."),
    model: modelArg,
    thinking: thinkingArg,
    reasoning_effort: reasoningEffortArg,
  },
  async ({ task, context, difficulty, output_type, constraints, model, thinking, reasoning_effort }) => {
    const taskDifficulty = difficulty || "medium";
    const result = await chat({
      tool: "deepseek_task",
      purpose: "task",
      difficulty: taskDifficulty,
      requestedModel: model,
      requestedThinking: thinking,
      requestedReasoningEffort: reasoning_effort,
      system:
        "You are DeepSeekHelper, a subordinate collaborator assisting Codex. You cannot read or write local files, run commands, or assume unstated project facts. Work only from the supplied context. For code changes, prefer file-scoped unified diff suggestions or concise snippets. For documentation and design, produce a directly usable draft. If the task appears high difficulty, unsafe, or under-specified, stop and explain what Codex should clarify or review first.",
      user: joinSections([
        `Task difficulty: ${taskDifficulty}`,
        `Preferred output: ${output_type || "choose the most useful format"}`,
        constraints ? `Constraints:\n${constraints}` : null,
        context ? `Context:\n${context}` : null,
        `Task:\n${task}`,
      ]),
    });

    return textResult("DeepSeekHelper delegated task result", result);
  }
);

server.tool(
  "deepseek_review",
  "Ask DeepSeek for an independent review of code changes, documentation, designs, prompts, or implementation notes.",
  {
    content: z.string().min(1).describe("The text, diff, plan, summary, or draft to review."),
    focus: z
      .string()
      .optional()
      .describe("Review focus, such as correctness, security, tests, factual accuracy, or clarity."),
    context: z.string().optional().describe("Relevant background context."),
    severity_style: z
      .enum(["brief", "ranked", "strict"])
      .optional()
      .describe("How strongly to classify findings."),
    model: modelArg,
    thinking: thinkingArg,
    reasoning_effort: reasoningEffortArg,
  },
  async ({ content, focus, context, severity_style, model, thinking, reasoning_effort }) => {
    const result = await chat({
      tool: "deepseek_review",
      purpose: "review",
      difficulty: "high",
      requestedModel: model,
      requestedThinking: thinking,
      requestedReasoningEffort: reasoning_effort,
      system:
        "You are an independent technical reviewer for Codex. Be concrete, skeptical, and concise. Report only verifiable issues, risks, omissions, and actionable fixes. Do not rewrite the whole artifact unless asked. If no issue is found, say so clearly and mention residual uncertainty.",
      user: joinSections([
        `Severity style: ${severity_style || "ranked"}`,
        `Review focus:\n${focus || "correctness, factual accuracy, missing edge cases, security risks, and test gaps"}`,
        context ? `Context:\n${context}` : null,
        `Material to review:\n${content}`,
      ]),
    });

    return textResult("DeepSeekHelper review", result);
  }
);

server.tool(
  "deepseek_discuss",
  "Ask DeepSeek to discuss a higher-difficulty implementation, documentation, or design decision with trade-offs.",
  {
    topic: z.string().min(1).describe("The decision or problem to discuss."),
    context: z.string().optional().describe("Relevant constraints, current design, code summary, or prior attempts."),
    options: z.string().optional().describe("Candidate options to compare."),
    decision_criteria: z.string().optional().describe("Criteria for choosing among options."),
    model: modelArg,
    thinking: thinkingArg,
    reasoning_effort: reasoningEffortArg,
  },
  async ({ topic, context, options, decision_criteria, model, thinking, reasoning_effort }) => {
    const result = await chat({
      tool: "deepseek_discuss",
      purpose: "discuss",
      difficulty: "high",
      requestedModel: model,
      requestedThinking: thinking,
      requestedReasoningEffort: reasoning_effort,
      system:
        "You are DeepSeekHelper, acting as a design and implementation discussion partner for Codex. Compare options, identify risks, surface hidden assumptions, and recommend a practical path. Keep the answer structured and do not claim access to files or tools.",
      user: joinSections([
        context ? `Context:\n${context}` : null,
        options ? `Options:\n${options}` : null,
        `Decision criteria:\n${decision_criteria || "correctness, maintainability, scope control, risk, and testability"}`,
        `Topic:\n${topic}`,
      ]),
    });

    return textResult("DeepSeekHelper discussion", result);
  }
);

server.tool(
  "deepseek_verify",
  "Ask DeepSeek to verify claims, assumptions, edge cases, test coverage, or risk analysis.",
  {
    claims: z.string().min(1).describe("Claims, assumptions, or conclusions to verify."),
    evidence: z.string().optional().describe("Evidence available to DeepSeek, such as logs, tests, docs, or code excerpts."),
    focus: z.string().optional().describe("Verification focus."),
    model: modelArg,
    thinking: thinkingArg,
    reasoning_effort: reasoningEffortArg,
  },
  async ({ claims, evidence, focus, model, thinking, reasoning_effort }) => {
    const result = await chat({
      tool: "deepseek_verify",
      purpose: "verify",
      difficulty: "high",
      requestedModel: model,
      requestedThinking: thinking,
      requestedReasoningEffort: reasoning_effort,
      system:
        "You are DeepSeekHelper verifying Codex's conclusions. Separate confirmed facts from assumptions. Identify unsupported claims, contradictions, missing evidence, and practical checks Codex should run next.",
      user: joinSections([
        `Verification focus:\n${focus || "accuracy, unsupported assumptions, missing checks, and residual risk"}`,
        evidence ? `Evidence:\n${evidence}` : null,
        `Claims to verify:\n${claims}`,
      ]),
    });

    return textResult("DeepSeekHelper verification", result);
  }
);

server.tool(
  "deepseek_prompt",
  "Ask DeepSeek to produce a strict prompt for a delegated task or independent review.",
  {
    objective: z.string().min(1).describe("What the prompt should accomplish."),
    context: z.string().optional().describe("Background context to include in the prompt."),
    target: z
      .enum(["task", "review", "discussion", "verification"])
      .optional()
      .describe("The kind of DeepSeek collaboration the prompt is for."),
    constraints: z.string().optional().describe("Rules or boundaries the prompt must include."),
    model: modelArg,
    thinking: thinkingArg,
    reasoning_effort: reasoningEffortArg,
  },
  async ({ objective, context, target, constraints, model, thinking, reasoning_effort }) => {
    const result = await chat({
      tool: "deepseek_prompt",
      purpose: "prompt",
      difficulty: "medium",
      requestedModel: model,
      requestedThinking: thinking,
      requestedReasoningEffort: reasoning_effort,
      system:
        "You are DeepSeekHelper writing strict, compact prompts for another model. Include role, context, task, constraints, output format, and failure conditions. Avoid vague language.",
      user: joinSections([
        `Target collaboration type: ${target || "task"}`,
        constraints ? `Constraints:\n${constraints}` : null,
        context ? `Context:\n${context}` : null,
        `Objective:\n${objective}`,
      ]),
    });

    return textResult("DeepSeekHelper prompt", result);
  }
);

await server.connect(new StdioServerTransport());
