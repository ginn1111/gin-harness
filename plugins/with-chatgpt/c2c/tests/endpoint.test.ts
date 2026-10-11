import { describe, it, expect } from "vitest";
import {
  connectorAction,
  connectorNameFor,
  DEFAULT_CONNECTOR_NAME,
  mcpUrlFromPublic,
  normalizePublicUrl,
  reclaimUserMessage,
} from "../src/config/endpoint.js";

describe("connectorAction", () => {
  it("creates on the first successful URL", () => {
    expect(connectorAction(null, "https://a.ngrok-free.app/mcp")).toBe("create");
  });

  it("is a no-op when the URL is unchanged", () => {
    expect(connectorAction("https://a.ngrok-free.app/mcp", "https://a.ngrok-free.app/mcp/")).toBe("none");
  });

  it("updates when the old address was reclaimed", () => {
    expect(connectorAction("https://old.ngrok-free.app/mcp", "https://new.ngrok-free.app/mcp")).toBe("update");
    expect(reclaimUserMessage("Hermes with ChatGPT")).toContain("Delete");
    expect(reclaimUserMessage("Hermes with ChatGPT")).not.toContain("Reconnect");
  });

  it("does nothing without a next URL", () => {
    expect(connectorAction("https://a.ngrok-free.app/mcp", null)).toBe("none");
  });
});

describe("connectorNameFor", () => {
  it("keeps a stored name for the same workspace", () => {
    expect(
      connectorNameFor({
        workspaceName: "EchoMind",
        workspaceId: "abc123abc123",
        previousName: "Hermes with ChatGPT",
        hadEndpointBefore: true,
      })
    ).toBe(DEFAULT_CONNECTOR_NAME);
  });

  it("keeps the legacy title when this workspace was used before the name field existed", () => {
    expect(
      connectorNameFor({
        workspaceName: "EchoMind",
        workspaceId: "abc123abc123",
        hadEndpointBefore: true,
      })
    ).toBe(DEFAULT_CONNECTOR_NAME);
  });

  it("gives a new workspace its own connector title", () => {
    expect(
      connectorNameFor({
        workspaceName: "Landing",
        workspaceId: "def456def456",
        hadEndpointBefore: false,
      })
    ).toBe("Hermes with ChatGPT · Landing");
  });
});

describe("mcpUrlFromPublic", () => {
  it("appends /mcp and folds case/slash variants", () => {
    expect(mcpUrlFromPublic("https://A.ngrok-free.app/")).toBe("https://a.ngrok-free.app/mcp");
    expect(mcpUrlFromPublic("https://a.ngrok-free.app/mcp")).toBe("https://a.ngrok-free.app/mcp");
    expect(normalizePublicUrl("https://A.ngrok-free.app/")).toBe("https://a.ngrok-free.app");
  });
});
