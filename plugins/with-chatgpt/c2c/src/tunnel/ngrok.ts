import { spawn, type ChildProcess } from "node:child_process";
import readline from "node:readline";
import type { Logger } from "../logger/index.js";
import { nullLogger } from "../logger/index.js";
import { SERVICE_NAME } from "../version.js";
import { findBinary } from "./detect.js";
import type { TunnelDoctorReport, TunnelProvider, TunnelStatus } from "./provider.js";

export const NGROK_INSTALL_HINT =
  "ngrok is not installed. Install it (macOS: `brew install ngrok`; Windows: `winget install ngrok.ngrok`), " +
  "add your authtoken with `ngrok config add-authtoken <token>`, then retry.";

const HEALTH_CHECK_INTERVAL_MS = 250;
const HEALTH_CHECK_TIMEOUT_MS = 5_000;
const DEFAULT_START_TIMEOUT_MS = readEnvInt("C2C_TUNNEL_START_TIMEOUT_MS", 90_000);

function readEnvInt(name: string, fallback: number): number {
  const raw = process.env[name];
  if (!raw) return fallback;
  const parsed = Number.parseInt(raw, 10);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

function isBridgeHealth(payload: unknown): boolean {
  if (!payload || typeof payload !== "object") return false;
  const health = payload as Record<string, unknown>;
  return health.service === SERVICE_NAME && health.status === "ok";
}

async function bridgeHealth(
  fetchImpl: NonNullable<NgrokTunnelOptions["fetchImpl"]>,
  publicUrl: string
): Promise<{ ready: boolean; detail: string }> {
  const response = await fetchImpl(new URL("/health", publicUrl).toString(), {
    redirect: "error",
    // Skips ngrok's free-tier browser interstitial for this probe.
    headers: { "ngrok-skip-browser-warning": "1" },
    signal: AbortSignal.timeout(HEALTH_CHECK_TIMEOUT_MS),
  });
  if (!response) return { ready: false, detail: "Health check did not run" };
  if (!response.ok) {
    await response.body?.cancel().catch(() => undefined);
    return { ready: false, detail: `Health check returned HTTP ${response.status}` };
  }
  return {
    ready: isBridgeHealth(await response.json().catch(() => null)),
    detail: `Health check did not identify ${SERVICE_NAME}`,
  };
}

/** Extract the public HTTPS URL from one ngrok JSON log line (`msg: "started tunnel"`). */
export function parseNgrokUrl(line: string): string | null {
  let entry: unknown;
  try {
    entry = JSON.parse(line);
  } catch {
    return null;
  }
  if (!entry || typeof entry !== "object") return null;
  const { msg, url } = entry as { msg?: unknown; url?: unknown };
  if (msg !== "started tunnel" || typeof url !== "string") return null;
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" ? parsed.origin : null;
  } catch {
    return null;
  }
}

export interface NgrokTunnelOptions {
  startTimeoutMs?: number;
  spawnImpl?: (
    command: string,
    args: string[],
    options: { stdio: ["ignore", "pipe", "pipe"]; windowsHide: true }
  ) => ChildProcess;
  fetchImpl?: (input: string | URL, init?: RequestInit) => Promise<Response>;
}

/**
 * ngrok ephemeral tunnel provider. Needs an ngrok authtoken; the HTTPS URL
 * changes on every start, which the bridge and the Skill handle by reconfiguring.
 */
export class NgrokTunnel implements TunnelProvider {
  readonly name = "ngrok";
  private child: ChildProcess | null = null;
  private url: string | null = null;
  private lastError: string | null = null;
  private readonly startTimeoutMs: number;
  private readonly spawnImpl: NonNullable<NgrokTunnelOptions["spawnImpl"]>;
  private readonly fetchImpl: NonNullable<NgrokTunnelOptions["fetchImpl"]>;
  private starting: Promise<string> | null = null;
  private cancelStart: (() => void) | null = null;

  constructor(
    private readonly logger: Logger = nullLogger,
    private readonly binaryOverride?: string,
    options: NgrokTunnelOptions = {}
  ) {
    this.startTimeoutMs = options.startTimeoutMs ?? DEFAULT_START_TIMEOUT_MS;
    this.spawnImpl = options.spawnImpl ?? ((command, args, spawnOptions) => spawn(command, args, spawnOptions));
    this.fetchImpl = options.fetchImpl ?? ((input, init) => fetch(input, init));
  }

  private binary(): string | null {
    return this.binaryOverride ?? findBinary("ngrok");
  }

  async start(localPort: number): Promise<string> {
    if (this.child && this.url) return this.url;
    if (this.starting) return this.starting;
    const starting = this.startProcess(localPort);
    this.starting = starting;
    try {
      return await starting;
    } finally {
      if (this.starting === starting) this.starting = null;
    }
  }

  private startProcess(localPort: number): Promise<string> {
    const bin = this.binary();
    if (!bin) return Promise.reject(new Error(NGROK_INSTALL_HINT));

    return new Promise<string>((resolve, reject) => {
      let child: ChildProcess;
      try {
        child = this.spawnImpl(
          bin,
          ["http", `127.0.0.1:${localPort}`, "--log", "stdout", "--log-format", "json"],
          { stdio: ["ignore", "pipe", "pipe"], windowsHide: true }
        );
      } catch (error) {
        reject(error);
        return;
      }
      this.child = child;
      this.url = null;
      this.lastError = null;
      let settled = false;
      let candidateUrl: string | null = null;
      let cancel: (() => void) | null = null;
      let timeout: ReturnType<typeof setTimeout> | undefined;

      const closeReaders = (): void => {
        child.stdout?.destroy();
        child.stderr?.destroy();
      };

      const isAlive = (): boolean => this.child === child;

      const stopChild = (): void => {
        try {
          child.kill("SIGTERM");
        } catch {
          // The process may have exited between the state check and kill().
        }
      };

      const finish = (callback: () => void, closeOutput = true): void => {
        if (settled) return;
        settled = true;
        if (timeout) clearTimeout(timeout);
        if (closeOutput) closeReaders();
        if (cancel && this.cancelStart === cancel) this.cancelStart = null;
        callback();
      };

      const fail = (error: unknown): void => {
        finish(() => {
          stopChild();
          if (this.child === child) {
            this.child = null;
            this.url = null;
          }
          reject(error instanceof Error ? error : new Error(String(error)));
        });
      };

      cancel = () => fail(new Error("Tunnel start stopped"));
      this.cancelStart = cancel;

      const ready = (url: string): void => {
        if (!isAlive()) {
          fail(new Error("ngrok exited before the public health endpoint became ready"));
          return;
        }
        finish(
          () => {
            this.url = url;
            this.lastError = null;
            this.logger.info(`ngrok tunnel established: ${url}`);
            resolve(url);
          },
          false
        );
      };

      const waitForHealth = async (): Promise<void> => {
        const publicUrl = candidateUrl;
        if (!publicUrl) return;
        while (!settled) {
          if (!isAlive()) {
            fail(new Error("ngrok exited before the public health endpoint became ready"));
            return;
          }
          try {
            const result = await bridgeHealth(this.fetchImpl, publicUrl);
            if (settled) return;
            if (result.ready) {
              ready(publicUrl);
              return;
            }
            this.lastError = result.detail;
            this.logger.warn(`ngrok tunnel not ready yet: ${result.detail}`);
          } catch (error) {
            if (settled) return;
            const cause = (error as { cause?: { code?: string; message?: string } }).cause;
            const causeText = cause ? ` (${cause.code ?? cause.message ?? "unknown cause"})` : "";
            this.lastError = error instanceof Error ? `${error.message}${causeText}` : String(error);
            this.logger.warn(`ngrok tunnel health check error: ${this.lastError}`);
          }
          if (settled) return;
          await new Promise((resolveWait) => setTimeout(resolveWait, HEALTH_CHECK_INTERVAL_MS));
        }
      };

      timeout = setTimeout(() => {
        if (!settled) {
          this.logger.error(`ngrok tunnel did not become ready within ${this.startTimeoutMs}ms`);
          fail(new Error("Tunnel start timed out"));
        }
      }, this.startTimeoutMs);

      const scan = (stream: NodeJS.ReadableStream): void => {
        const rl = readline.createInterface({ input: stream });
        rl.on("line", (line) => {
          const url = parseNgrokUrl(line);
          if (url && !candidateUrl) {
            candidateUrl = url;
            void waitForHealth().catch((error) => {
              this.logger.error(`ngrok tunnel health check failed: ${String(error)}`);
            });
          }
          if (/\b(?:ERR|error|failed|fatal)\b/i.test(line)) {
            this.lastError = line.slice(0, 400);
            this.logger.debug(`ngrok: ${line.slice(0, 400)}`);
          }
        });
      };
      if (child.stdout) scan(child.stdout);
      if (child.stderr) scan(child.stderr);

      child.on("error", (error) => {
        closeReaders();
        if (this.child === child) {
          this.child = null;
          this.url = null;
        }
        if (!settled) fail(error);
      });
      child.on("exit", (code) => {
        closeReaders();
        if (this.child === child) {
          this.child = null;
          this.url = null;
          this.lastError = `ngrok exited (code ${code})`;
        }
        this.logger.warn(`ngrok exited with code ${code}`);
        if (!settled) {
          fail(
            new Error(
              `ngrok exited (code ${code}) before establishing a tunnel${this.lastError ? `: ${this.lastError}` : ""}`
            )
          );
        }
      });
    });
  }

  async stop(): Promise<void> {
    this.cancelStart?.();
    if (this.child) {
      try {
        this.child.kill("SIGTERM");
      } catch {
        // The process may have exited between the state check and kill().
      }
      this.child = null;
    }
    this.url = null;
    this.lastError = null;
  }

  async restart(localPort: number): Promise<string> {
    await this.stop();
    return this.start(localPort);
  }

  status(): TunnelStatus {
    return {
      running: this.child !== null && this.url !== null,
      url: this.url,
      provider: this.name,
      detail: this.lastError ?? undefined,
    };
  }

  getPublicUrl(): string | null {
    return this.url;
  }

  async doctor(): Promise<TunnelDoctorReport> {
    const bin = this.binary();
    const problems: string[] = [];
    if (!bin) problems.push(NGROK_INSTALL_HINT);
    if (bin && !this.child) problems.push("tunnel process not running");
    if (this.child && !this.url) problems.push("tunnel running but no public URL yet");
    return {
      provider: this.name,
      binaryFound: bin !== null,
      binaryPath: bin,
      running: this.child !== null,
      url: this.url,
      problems,
    };
  }
}
