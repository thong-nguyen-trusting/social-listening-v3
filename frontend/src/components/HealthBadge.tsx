import { Stack, Text } from "@mantine/core";
import { useEffect, useState } from "react";
import { KeyValueRow } from "./ui/KeyValueRow";
import { PageHeader } from "./ui/PageHeader";
import { PageSection } from "./ui/PageSection";
import { StatusBadge } from "./ui/StatusBadge";
import { apiUrl } from "../lib/api";

type HealthStatus = {
  status: "HEALTHY" | "CAUTION" | "BLOCKED";
  cooldown_until: string | null;
  last_signal: { type: string; detected_at: string } | null;
};

const fallback: HealthStatus = {
  status: "HEALTHY",
  cooldown_until: null,
  last_signal: null,
};

export function HealthBadge() {
  const [status, setStatus] = useState<HealthStatus>(fallback);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const response = await fetch(apiUrl("/api/health/status"));
        if (!response.ok) {
          return;
        }
        const payload = (await response.json()) as HealthStatus;
        if (!cancelled) {
          setStatus(payload);
        }
      } catch {
        if (!cancelled) {
          setStatus(fallback);
        }
      }
    };

    load();
    const id = window.setInterval(load, 5000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  return (
    <PageSection>
      <PageHeader
        description="Live account safety signal and cooldown state."
        eyebrow="Health"
        title="Health monitor"
      />
      <Stack gap="sm">
        <StatusBadge label={`Health ${status.status}`} status={status.status} withDot />
        {status.cooldown_until ? (
          <KeyValueRow label="Cooldown until" mono value={status.cooldown_until} />
        ) : (
          <Text c="dimmed" size="sm">
            No active cooldown.
          </Text>
        )}
        {status.last_signal ? (
          <>
            <KeyValueRow label="Last signal" value={status.last_signal.type} />
            <KeyValueRow label="Detected at" mono value={status.last_signal.detected_at} />
          </>
        ) : (
          <Text c="dimmed" size="sm">
            No active risk signal.
          </Text>
        )}
      </Stack>
    </PageSection>
  );
}
