import path from "node:path";
import { getStateDir, readJsonIfExists, writeSecureJson } from "../config/paths.js";

export type TunnelPreference = "unset" | "quick" | "named";

export interface TunnelState {
  workspaceId: string;
  preference: TunnelPreference;
  askedAt?: string;
  provider?: "cloudflare-quick" | "cloudflare-named";
  tunnelName?: string;
  tunnelId?: string;
  hostname?: string;
  zone?: string;
  configuredAt?: string;
  fallbackReason?: string;
}

export function tunnelStateFile(workspaceId: string): string {
  return path.join(getStateDir(), "tunnels", `${workspaceId}.json`);
}

export function readTunnelState(workspaceId: string): TunnelState {
  return (
    readJsonIfExists<TunnelState>(tunnelStateFile(workspaceId)) ?? {
      workspaceId,
      preference: "unset",
    }
  );
}

export function writeTunnelState(state: TunnelState): TunnelState {
  writeSecureJson(tunnelStateFile(state.workspaceId), state);
  return state;
}

export function needsTunnelChoice(state: TunnelState): boolean {
  return state.preference === "unset" || !state.askedAt;
}

export function isNamedTunnelReady(state: TunnelState): boolean {
  return (
    state.preference === "named" &&
    Boolean(state.tunnelName?.trim()) &&
    Boolean(state.hostname?.trim())
  );
}

export function namedTunnelBinding(state: TunnelState): { tunnelName: string; hostname: string } | null {
  if (!isNamedTunnelReady(state) || !state.tunnelName || !state.hostname) return null;
  return { tunnelName: state.tunnelName, hostname: state.hostname };
}

export const TUNNEL_CHOICE_PROMPT = `Before connecting ChatGPT there is one optional choice.
Do you have a Cloudflare account with a domain already added to Cloudflare?
- Yes: use a fixed domain. Configure the connector once; it usually needs no change after a restart. You log in to Cloudflare once and add a subdomain under your domain.
- No: use a temporary address. No sign-up and the same features, but the address often changes after a restart and the old address in ChatGPT stops working. Hermes removes this project's connector and adds it back with the new address; you may need to sign in to ChatGPT again. It is recoverable, just slower.
No account is fully supported. Which do you choose? If you have a domain, tell me the domain (for example example.com).`;

export const NAMED_LOGIN_PROMPT =
  "A browser will open. Log in to Cloudflare and select your domain, then tell me \"done\".";

export const NAMED_FALLBACK_MESSAGE =
  "Using a temporary address this time. Features are the same, but repairing the connection later may be slower. Tell me when you want to switch to a fixed domain.";

export const NAMED_REPAIR_MESSAGE =
  "The fixed domain is temporarily unreachable. Log in to Cloudflare in the window that opens and select your domain, then tell me \"done\".";
