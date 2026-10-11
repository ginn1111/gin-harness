/**
 * Tunnel abstraction. Business logic never talks to a specific vendor;
 * it only sees this interface. V1 ships an ngrok ephemeral tunnel provider.
 */
export interface TunnelStatus {
  running: boolean;
  url: string | null;
  provider: string;
  detail?: string;
}

export interface TunnelDoctorReport {
  provider: string;
  binaryFound: boolean;
  binaryPath: string | null;
  running: boolean;
  url: string | null;
  problems: string[];
}

export interface TunnelProvider {
  readonly name: string;
  /** Start the tunnel for a local port; resolves with the public URL. */
  start(localPort: number): Promise<string>;
  stop(): Promise<void>;
  restart(localPort: number): Promise<string>;
  status(): TunnelStatus;
  getPublicUrl(): string | null;
  doctor(): Promise<TunnelDoctorReport>;
}
