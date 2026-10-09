# Hermes with ChatGPT

> ChatGPT plans and reviews. Hermes executes.
> ChatGPT 负责规划和审查，Hermes 负责执行。

> [!IMPORTANT]
> **遇到问题？** 请先向 Hermes 发送 **「更新 Hermes with ChatGPT」** 并重试。更新到最新版本可以解决大多数已知问题。
> **Having trouble?** First ask Hermes to **“Update Hermes with ChatGPT”** and try again. Updating to the latest version resolves most known issues.

## The problem · 解决什么问题

**中文** — ChatGPT 付费订阅的网页版额度大量闲置，Hermes 却在消耗紧张的
API 额度做规划和 Review。本项目把规划交给你已付费的网页版 ChatGPT，
Hermes 只负责执行。不用 API Key、不搞逆向代理——官方网页 + 只读 MCP 桥接。

**EN** — ChatGPT Plus/Pro web quota sits idle while Hermes burns scarce API
tokens on planning and review. This project moves planning to the subscription
you already pay for; Hermes only executes.
No API keys, no reverse proxy — official web UI plus a read-only MCP bridge.

## What it is · 这是什么

**中文** — 把 ChatGPT 网页版变成 Hermes 编码会话的"规划与审查大脑"，执行权
完全保留在 Hermes 手里。你的仓库永远不会被上传：ChatGPT 通过一条安全的、
OAuth 保护的**只读** MCP 连接，按需读取当前工作区里它真正需要的那几行代码。

**EN** — Use the ChatGPT web app as the planning and review brain for your
Hermes coding sessions, while Hermes keeps full ownership of execution. Your
repository is never uploaded: ChatGPT reads exactly the lines it needs through
a secure, OAuth-protected, **read-only** MCP connection to your current
workspace.

Detailed docs below are in English · 详细中文文档见 **[README.zh-CN.md](README.zh-CN.md)**

## One-paste install · 一段话安装

**中文** — 不懂 git、Node、终端？完全不需要懂。把下面这段话原样复制给你的
编码 Agent（Hermes），然后去倒杯咖啡：

```text
请帮我完整安装并配置 Hermes with ChatGPT，全程自动，我是不懂技术的小白，
所有事情你自己做：

1. 环境自检：需要 git 和 Node.js ≥ 20，缺什么就自动安装
  （macOS 用 Homebrew，Windows 用 winget），同时安装 cloudflared。
2. 下载：把 Hermes with ChatGPT 仓库克隆到
   ~/hermes-with-chatgpt（已存在就 git pull 更新）。
3. 构建：在该目录里执行 corepack pnpm install 和 corepack pnpm build。
4. 安装 Skill：将插件安装到 Hermes profile。不要修改旧版宿主配置或路径。
   Hermes 通过原生插件 API 提供 C2C 和 terminal-browser 指引。
5. 首次配置：按 SKILL.md 里的 first-time setup 流程执行
  （运行 c2c setup，用内置浏览器打开 ChatGPT 配置连接器并输入配对码）。
   全程只用内置浏览器，禁止打开任何第三方浏览器。
6. 只有遇到需要我登录（ChatGPT / Cloudflare）、验证码或两步验证时才叫我，
   而且一次只告诉我一个动作。
7. 完成后给我看 ✓ 清单，并确认文件读取测试通过。我不懂 MCP、OAuth、
   Tunnel、端口这些词，不要向我解释；出了问题先自己修。
```


**EN** — Don't know git, Node, or terminals? You don't need to. Copy the
paragraph below, paste it to your coding agent (Hermes), and go grab a coffee:

```text
Please install and configure "Hermes with ChatGPT" for me, fully automatically.
I am a non-technical user — do everything yourself:

1. Check the environment: git and Node.js >= 20 must be available. Install
   anything missing yourself (macOS: Homebrew, Windows: winget). Also install
   cloudflared.
2. Download the Hermes with ChatGPT checkout into
   ~/hermes-with-chatgpt (if it already exists, update it in place).
3. Build: inside that folder run `corepack pnpm install` then `corepack pnpm build`.
4. Install the plugin into a Hermes profile. Do not modify legacy host
   configuration or paths. Hermes exposes the C2C and terminal-browser guidance
   through native plugin APIs.
5. First-time setup: follow the SKILL.md "first-time setup" workflow
   (run c2c setup, configure the ChatGPT connector in the BUILT-IN browser,
   enter the pairing code). Never open a third-party browser.
6. Only interrupt me for logins (ChatGPT / Cloudflare), CAPTCHAs or 2FA —
   and give me exactly ONE action at a time.
7. When done, show me the ✓ checklist and confirm the file-read test passed.
   I don't know what MCP, OAuth, tunnels or ports are. Don't explain them.
   If anything breaks, fix it yourself first.
```


**Updates · 更新** — Update the Hermes plugin through its profile installer.
The plugin does not silently mutate profile identity, authentication, or runtime state.

---

*The sections below are in English. 以下详细内容为英文，中文完整版见
[README.zh-CN.md](README.zh-CN.md)。*

## Install → Setup → Use (manual)

Install this plugin into a Hermes profile with the Gin-harness installer.
Hermes provides `c2c` and the namespaced workflow skills through native plugin
APIs. Collaboration remains disabled until explicitly enabled for a session.

1. Run `make install PROFILES="<profile>"` from the setup repository.
2. Enable the current session with `hermes with-chatgpt enable --session-id <id>`.
3. Use `hermes with-chatgpt setup`, then follow the explicit C2C skill workflow.

> **Installation scope:** This plugin does not publish a Web GPT, launcher, or
> model-catalog entry. It does not modify legacy host configuration. `terminal-browser`
> remains an external prerequisite. For runtime details, see [troubleshooting](docs/troubleshooting.md).

That's the whole manual. Setup and doctor report actionable state; doctor is
read-only unless `--repair` is explicitly passed.

```
Hermes with ChatGPT",

✓ Project detected
✓ Workspace Bridge started
✓ Secure connection established
✓ ChatGPT connected
✓ File read test passed

Ready.
```

The only steps that may need you: logging into ChatGPT or Cloudflare, plus
confirmation before consequential browser actions. Existing workspace
connectors and resumable C2C checkpoints are reused; no conversation or
connector is silently replaced.

### Optional stable hostname

The default public address is a temporary Cloudflare URL. It can change when
the bridge restarts. Doctor reports connector repair explicitly; it never
silently churns a healthy connector.

Named tunnels remain optional. If you choose one, Cloudflare authorization
happens only through the explicit external workflow. Credentials stay in the
OS app state directory, not in the project.

## How it works

```
             ┌───────────────────────────┐
             │       ChatGPT Web         │
             │  Reason / Plan / Review   │
             └──────────┬──────────▲─────┘
                        │          │
               MCP      │          │ Computer Use
            Data Plane  │          │ Control Plane (<1 KB messages)
                        ▼          │
             ┌─────────────────────┐
             │      C2C Bridge     │   loopback-only HTTP server
             │  read-only MCP      │   OAuth 2.1 + one-time pairing code
             │  OAuth + Pairing    │   Cloudflare Quick Tunnel
             │  Tunnel Manager     │
             └──────────┬──────────┘
                        │  read-only
                        ▼
             ┌─────────────────────┐          ┌─────────────────────┐
             │   Local Workspace   │◀─────────│    Hermes Runtime   │
             └─────────────────────┘ edit/git │ shell / tests / fix │
                                              └─────────────────────┘
```

- **Control plane (explicit browser workflow)**: Hermes and ChatGPT exchange tiny structured
  `[C2C]` state messages — `INIT → PLAN → EXECUTED → REVIEW → DONE`. No diffs,
  no logs, no file bodies are ever pasted.
- **Data plane (MCP)**: ChatGPT pulls what it needs itself through 10 read-only
  tools: `workspace_info`, `list_directory`, `read_file`, `search_workspace`,
  `git_status`, `git_diff`, `test_status`, `execution_summary`,
  `execution_output`, `read_image`.
- **Independent review**: after Hermes executes, ChatGPT inspects the actual
  git diff and test records through MCP — it never trusts "all tests passed"
  claims blindly.

### Generated media handoff

The connector remains read-only: `read_image` can inspect supported workspace
images but cannot write files. After a requested image or video is downloaded
through the visible ChatGPT UI, the local executor can validate and import the
original with `c2c asset import -w <workspace> --from <download> --to <new-path>`.
Imports are workspace-contained, signature-checked, size-limited, reject active
SVG content, and never overwrite an existing file.

## Security model (short version)

- **Read-only by construction**: write/delete/shell/commit tools simply do not
  exist on the server. No prompt injection can enable them.
- **One workspace = one boundary**: every token is bound to a single workspace;
  path containment uses canonical realpaths (symlink/`../`/absolute-path escapes
  are all blocked and tested).
- **Sensitive files never leave**: `.env*`, keys, SSH, credentials are denied by
  default (`.env.example` allowed); `.c2cignore` adds your own rules.
- **Knowing the URL grants nothing**: the public MCP endpoint requires OAuth 2.1
  (PKCE S256, dynamic client registration, rotating refresh tokens). Without a
  token: 401. Wrong workspace: 403.
- **The model never sees long-lived credentials**: the only secret that ever
  touches a browser is a one-time pairing code (5-minute TTL, 5 attempts,
  rate-limited, destroyed on use).

Full threat model: [docs/security.md](docs/security.md)

## For developers

```bash
pnpm install
pnpm build          # -> dist/, exposes the `c2c` bin
pnpm test           # vitest: 150 tests (path security, OAuth, pairing, MCP e2e)

c2c setup           # bridge + tunnel + pairing code, all in one
c2c sandbox-allow   # explicit legacy compatibility command (macOS + Windows)
c2c status / doctor / pair / unpair / logs / stop
```

Requirements: Node.js >= 20, git. `cloudflared` for the public connection
(auto-detected; the Skill installs it for you). If QUIC is blocked, set
`C2C_TUNNEL_PROTOCOL=http2` and restart the bridge.

Docs: [architecture](docs/architecture.md) · [protocol](docs/protocol.md) ·
[security](docs/security.md) · [troubleshooting](docs/troubleshooting.md)

## Project layout

```
src/
  bridge/     loopback HTTP server, port recovery, admin API
  mcp/        9 read-only tools, stateless Streamable HTTP
  auth/       OAuth 2.1 (PKCE, DCR, refresh rotation, revocation)
  pairing/    one-time pairing codes (CSPRNG, TTL, rate limits)
  workspace/  path containment, sensitive-file policy, search, git
  tunnel/     TunnelProvider abstraction + Cloudflare Quick/Named Tunnel
  execution/  execution records for the review loop
  process/    daemon lifecycle
  cli/        the c2c CLI
skill/        the C2C skill (the real UX layer)
tests/        unit + integration tests
docs/         architecture / protocol / security / troubleshooting
```

## Status & disclaimer

V1. Verified end-to-end: bridge, OAuth + pairing, public tunnel, ChatGPT
connector setup, zero-touch first-run experience.

**Unofficial community project. Not affiliated with or endorsed by OpenAI.**

## License

[MIT](LICENSE)

## Star History

<!-- Star History omitted: this setup repository is not the upstream project. -->
