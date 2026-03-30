import {
  Alert,
  Button,
  Paper,
  Stack,
  Text,
  TextInput,
} from "@mantine/core";
import { useEffect, useState } from "react";
import { ActionBar } from "../components/ui/ActionBar";
import { KeyValueRow } from "../components/ui/KeyValueRow";
import { PageHeader } from "../components/ui/PageHeader";
import { PageSection } from "../components/ui/PageSection";
import { StatusBadge } from "../components/ui/StatusBadge";
import { fetchJson } from "../lib/api";

type PlanStep = {
  step_id: string;
  action_type: string;
  read_or_write: string;
  target: string;
  estimated_count: number | null;
  risk_level: string;
  dependency_step_ids: string[];
  explain?: string;
};

type PlanResponse = {
  plan_id: string;
  context_id: string;
  version: number;
  steps: PlanStep[];
  estimated_total_duration_sec?: number;
  warnings?: string[];
  diff_summary?: string | null;
};

type PlanPageProps = {
  initialContextId?: string;
  onPlanReady?: (planId: string) => void;
};

export function PlanPage({ initialContextId = "", onPlanReady }: PlanPageProps) {
  const [contextId, setContextId] = useState("");
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [instruction, setInstruction] = useState("chi crawl 2 groups thoi");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setContextId(initialContextId);
    setPlan(null);
    setError("");
  }, [initialContextId]);

  const generate = async () => {
    setIsGenerating(true);
    setError("");
    try {
      const payload = await fetchJson<PlanResponse>("/api/plans", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ context_id: contextId.trim() }),
      });
      setPlan(payload);
      onPlanReady?.(payload.plan_id);
    } catch (requestError) {
      setPlan(null);
      setError(requestError instanceof Error ? requestError.message : "Generate plan failed");
    } finally {
      setIsGenerating(false);
    }
  };

  const refine = async () => {
    if (!plan) return;
    setIsRefining(true);
    setError("");
    try {
      const payload = await fetchJson<PlanResponse>(`/api/plans/${plan.plan_id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ instruction }),
      });
      setPlan(payload);
      onPlanReady?.(payload.plan_id);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Refine plan failed");
    } finally {
      setIsRefining(false);
    }
  };

  return (
    <PageSection>
      <PageHeader
        description="Generate ordered execution steps and highlight write actions clearly."
        eyebrow="Plan generation"
        title="Ordered steps with write action highlights."
      />
      <Stack gap="sm">
        <TextInput
          onChange={(event) => setContextId(event.target.value)}
          placeholder="Enter context_id from keyword step"
          value={contextId}
        />
        <ActionBar>
          <Button onClick={generate} disabled={isGenerating || isRefining || !contextId.trim()}>
            {isGenerating ? "Generating..." : "Generate Plan"}
          </Button>
          <Button onClick={refine} disabled={isGenerating || isRefining || !plan} variant="light">
            {isRefining ? "Refining..." : "Refine Plan"}
          </Button>
        </ActionBar>
        <TextInput
          onChange={(event) => setInstruction(event.target.value)}
          placeholder="Natural language refinement"
          value={instruction}
        />
        {error ? (
          <Alert color="red" variant="light">
            {error}
          </Alert>
        ) : null}
        {contextId ? <KeyValueRow label="using context_id" mono value={contextId} /> : null}
        {plan ? (
          <Stack gap="sm">
            <KeyValueRow label="plan_id" mono value={plan.plan_id} />
            <KeyValueRow label="version" value={plan.version} />
            {plan.diff_summary ? <KeyValueRow label="diff" value={plan.diff_summary} /> : null}
            {plan.warnings?.map((warning) => (
              <Alert color="yellow" key={warning} variant="light">
                {warning}
              </Alert>
            ))}
            {plan.steps.map((step) => (
              <Paper
                key={step.step_id}
                p="sm"
                radius="md"
                style={
                  step.read_or_write === "WRITE"
                    ? { borderColor: "var(--mantine-color-red-3)" }
                    : undefined
                }
                withBorder
              >
                <Stack gap={6}>
                  <Text fw={700} size="sm">
                    {step.step_id} · {step.action_type}
                  </Text>
                  <StatusBadge status={step.read_or_write} />
                  <Text c="dimmed" size="sm">
                    risk {step.risk_level}
                  </Text>
                  {step.explain ? (
                    <Alert color="blue" variant="light">
                      {step.explain}
                    </Alert>
                  ) : null}
                  <KeyValueRow label="target" value={step.target} />
                  <KeyValueRow
                    label="dependencies"
                    value={step.dependency_step_ids.join(", ") || "none"}
                  />
                </Stack>
              </Paper>
            ))}
          </Stack>
        ) : null}
      </Stack>
    </PageSection>
  );
}
