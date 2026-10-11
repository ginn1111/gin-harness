import { describe, it, expect, afterEach, vi } from "vitest";
import { EventEmitter } from "node:events";
import fs from "node:fs";
import type { ChildProcess } from "node:child_process";
import { PassThrough } from "node:stream";
import { findBinary } from "../src/tunnel/detect.js";
import { NgrokTunnel, parseNgrokUrl, type NgrokTunnelOptions } from "../src/tunnel/ngrok.js";
import { cleanup, makeTmpDir, write } from "./helpers.js";

const stateDirs: string[] = [];
const previousNgrokPath = process.env.C2C_NGROK_PATH;
const PUBLIC_URL = "https://random-words-1234.ngrok-free.app";
type FetchImpl = NonNullable<NgrokTunnelOptions["fetchImpl"]>;

class FakeNgrokProcess extends EventEmitter {
  readonly stdout = new PassThrough();
  readonly stderr = new PassThrough();
  exitCode: number | null = null;
  signalCode: NodeJS.Signals | null = null;
  killed = false;
  readonly kill = vi.fn(() => {
    this.killed = true;
    return true;
  });
}

function setupTunnel(fetchImpl: FetchImpl, startTimeoutMs = 1_000) {
  const child = new FakeNgrokProcess();
  const spawnImpl = vi.fn(() => child as unknown as ChildProcess);
  const tunnel = new NgrokTunnel(undefined, "ngrok", { spawnImpl, fetchImpl, startTimeoutMs });
  return { child, spawnImpl, tunnel };
}

function announceUrl(child: FakeNgrokProcess): void {
  child.stdout.write(`${JSON.stringify({ lvl: "info", msg: "started tunnel", url: PUBLIC_URL })}\n`);
}

function healthResponse(): Response {
  return new Response(JSON.stringify({ service: "c2c-bridge", status: "ok" }), { status: 200 });
}

afterEach(() => {
  while (stateDirs.length) cleanup(stateDirs.pop()!);
  if (previousNgrokPath === undefined) delete process.env.C2C_NGROK_PATH;
  else process.env.C2C_NGROK_PATH = previousNgrokPath;
});

describe("findBinary", () => {
  it("uses C2C_NGROK_PATH for an accessible ngrok executable", () => {
    const dir = makeTmpDir("ngrok-path");
    stateDirs.push(dir);
    const filename = process.platform === "win32" ? "ngrok.exe" : "ngrok";
    const configured = write(dir, filename, "placeholder");
    if (process.platform !== "win32") fs.chmodSync(configured, 0o755);
    process.env.C2C_NGROK_PATH = configured;
    expect(findBinary("ngrok")).toBe(configured);
  });
});

describe("parseNgrokUrl", () => {
  it("extracts the HTTPS URL from the ngrok JSON log", () => {
    const line = JSON.stringify({ lvl: "info", msg: "started tunnel", obj: "tunnels", url: PUBLIC_URL });
    expect(parseNgrokUrl(line)).toBe(PUBLIC_URL);
  });

  it("ignores unrelated lines, non-HTTPS URLs and malformed input", () => {
    expect(parseNgrokUrl("not json")).toBeNull();
    expect(parseNgrokUrl(JSON.stringify({ msg: "client session established" }))).toBeNull();
    expect(parseNgrokUrl(JSON.stringify({ msg: "started tunnel", url: "tcp://0.tcp.ngrok.io:1234" }))).toBeNull();
  });
});

describe("NgrokTunnel", () => {
  it("resolves only after the public health endpoint identifies the bridge", async () => {
    const fetchImpl = vi.fn(async () => healthResponse());
    const { child, spawnImpl, tunnel } = setupTunnel(fetchImpl);
    const starting = tunnel.start(3333);
    announceUrl(child);

    await expect(starting).resolves.toBe(PUBLIC_URL);
    expect(spawnImpl).toHaveBeenCalledWith(
      "ngrok",
      ["http", "127.0.0.1:3333", "--log", "stdout", "--log-format", "json"],
      { stdio: ["ignore", "pipe", "pipe"], windowsHide: true }
    );
    expect(fetchImpl).toHaveBeenCalledWith(`${PUBLIC_URL}/health`, {
      redirect: "error",
      headers: { "ngrok-skip-browser-warning": "1" },
      signal: expect.any(AbortSignal),
    });
    expect(tunnel.status()).toMatchObject({ running: true, url: PUBLIC_URL });
    await tunnel.stop();
  });

  it("keeps consuming ngrok errors after the tunnel is ready", async () => {
    const { child, tunnel } = setupTunnel(async () => healthResponse());
    const starting = tunnel.start(3333);
    announceUrl(child);
    await expect(starting).resolves.toBe(PUBLIC_URL);

    child.stderr.write("ERR runtime connection error\n");
    await new Promise((resolve) => setImmediate(resolve));
    expect(tunnel.status().detail).toBe("ERR runtime connection error");
    await tunnel.stop();
  });

  it("does not accept an HTTP 200 response from another service", async () => {
    const { child, tunnel } = setupTunnel(
      async () =>
        new Response(JSON.stringify({ service: "other", status: "ok" }), { status: 200 }),
      20
    );
    const starting = tunnel.start(3333);
    announceUrl(child);

    await expect(starting).rejects.toThrow(/timed out/i);
    expect(child.kill).toHaveBeenCalledWith("SIGTERM");
    expect(tunnel.status()).toMatchObject({ running: false, url: null });
  });

  it("does not spawn twice or resolve a stopped pending start", async () => {
    const { child, spawnImpl, tunnel } = setupTunnel(() => new Promise<Response>(() => {}));
    const starting = tunnel.start(3333);
    announceUrl(child);
    await new Promise((resolve) => setImmediate(resolve));

    const concurrent = tunnel.start(3333);
    await tunnel.stop();
    await expect(starting).rejects.toThrow(/stopped/i);
    await expect(concurrent).rejects.toThrow(/stopped/i);
    expect(spawnImpl).toHaveBeenCalledTimes(1);
    expect(child.kill).toHaveBeenCalledWith("SIGTERM");
  });

  it("does not resolve if ngrok exits while the health probe is in flight", async () => {
    let resolveFetch!: (response: Response) => void;
    const { child, tunnel } = setupTunnel(
      () => new Promise<Response>((resolve) => (resolveFetch = resolve))
    );
    const starting = tunnel.start(3333);
    announceUrl(child);
    await new Promise((resolve) => setImmediate(resolve));

    child.exitCode = 1;
    child.emit("exit", 1, null);
    resolveFetch(healthResponse());
    await expect(starting).rejects.toThrow(/exited/i);
    expect(tunnel.status()).toMatchObject({ running: false, url: null });
  });

  it("rejects when spawning reports an asynchronous error", async () => {
    const { child, tunnel } = setupTunnel(async () => new Response(null));
    const starting = tunnel.start(3333);
    await new Promise((resolve) => setImmediate(resolve));
    child.emit("error", new Error("spawn ngrok ENOENT"));

    await expect(starting).rejects.toThrow(/ENOENT/i);
    expect(tunnel.status()).toMatchObject({ running: false, url: null });
  });

  it("retries a non-ready health response before resolving", async () => {
    let calls = 0;
    const cancelBody = vi.fn(async () => undefined);
    const { child, tunnel } = setupTunnel(async () => {
      calls += 1;
      return calls === 1
        ? ({ ok: false, status: 503, body: { cancel: cancelBody } } as unknown as Response)
        : healthResponse();
    });
    const starting = tunnel.start(3333);
    announceUrl(child);

    await expect(starting).resolves.toBe(PUBLIC_URL);
    expect(calls).toBe(2);
    expect(cancelBody).toHaveBeenCalledTimes(1);
    await tunnel.stop();
  });
});

describe("ngrok install guidance", () => {
  it("rejects start and reports it in doctor when ngrok is missing", async () => {
    const dir = makeTmpDir("ngrok-missing");
    stateDirs.push(dir);
    const tunnel = new NgrokTunnel(undefined, undefined, {});
    const prevPath = process.env.PATH;
    const prevHome = process.env.HOME;
    process.env.PATH = dir;
    try {
      if (findBinary("ngrok")) return; // present in a common install dir on this machine
      await expect(tunnel.start(3333)).rejects.toThrow(/brew install ngrok/);
      const report = await tunnel.doctor();
      expect(report.binaryFound).toBe(false);
      expect(report.problems[0]).toContain("brew install ngrok");
    } finally {
      process.env.PATH = prevPath;
      process.env.HOME = prevHome;
    }
  });
});
