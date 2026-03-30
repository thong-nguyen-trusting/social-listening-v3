import {
  Alert,
  Button,
  Checkbox,
  Paper,
  Stack,
  Text,
  TextInput,
} from "@mantine/core";
import { useEffect, useMemo, useState } from "react";
import { ActionBar } from "../components/ui/ActionBar";
import { PageHeader } from "../components/ui/PageHeader";
import { PageSection } from "../components/ui/PageSection";
import { fetchJson } from "../lib/api";

type PlanStep = {
  step_id: string;
  action_type: string;
  read_or_write: string;
  dependency_step_ids: string[];
};

type PlanResponse = {
  plan_id: string;
  steps: PlanStep[];
};

type ApprovalResponse = {
  grant_id: string;
  approved_step_ids: string[];
  plan_version: number;
  approver_id: string;
  approved_at: string;
};

type RunResponse = {
  run_id: string;
  status: string;
};

type ApprovePageProps = {
  initialPlanId?: string;
  onRunReady?: (runId: string) => void;
};

export function ApprovePage({ initialPlanId = "", onRunReady }: ApprovePageProps) {
  const [planId, setPlanId] = useState("");
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [statusMessage, setStatusMessage] = useState("");
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [isStartingRun, setIsStartingRun] = useState(false);
  const [error, setError] = useState("");

  const dependencyWarning = useMemo(() => {
    if (!plan) return "";
    const selectedSet = new Set(selected);
    const broken = plan.steps.find((step) =>
      step.dependency_step_ids.some((dep) => !selectedSet.has(dep)) && selectedSet.has(step.step_id)
    );
    return broken ? `Dependency warning: ${broken.step_id} depends on ${broken.dependency_step_ids.join(", ")}` : "";
  }, [plan, selected]);

  const loadPlanById = async (nextPlanId: string) => {
    const normalizedPlanId = nextPlanId.trim();
    if (!normalizedPlanId) return;
    setIsLoadingPlan(true);
    setError("");
    try {
      const payload = await fetchJson<PlanResponse>(`/api/plans/${normalizedPlanId}`);
      setPlan(payload);
      setPlanId(payload.plan_id);
      setSelected(payload.steps.map((step) => step.step_id));
      setStatusMessage(`Plan loaded. ${payload.steps.length} steps ready for review.`);
    } catch (requestError) {
      setPlan(null);
      setSelected([]);
      setStatusMessage("");
      setError(requestError instanceof Error ? requestError.message : "Load plan failed");
    } finally {
      setIsLoadingPlan(false);
    }
  };

  useEffect(() => {
    if (!initialPlanId) {
      setPlanId("");
      setPlan(null);
      setSelected([]);
      setStatusMessage("");
      setError("");
      return;
    }
    if (initialPlanId === planId) {
      return;
    }
    setPlanId(initialPlanId);
    void loadPlanById(initialPlanId);
  }, [initialPlanId]);

  const loadPlan = async () => {
    await loadPlanById(planId);
  };

  const toggleStep = (stepId: string) => {
    setSelected((current) =>
      current.includes(stepId) ? current.filter((item) => item !== stepId) : [...current, stepId]
    );
  };

  const approve = async () => {
    setIsApproving(true);
    setIsStartingRun(false);
    setError("");
    setStatusMessage("Submitting approval...");
    try {
      const approval = await fetchJson<ApprovalResponse>(`/api/plans/${planId}/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step_ids: selected }),
      });
      setStatusMessage(
        `Approval received. grant_id: ${approval.grant_id} · ${approval.approved_step_ids.length} steps approved`
      );
      setIsStartingRun(true);
      const run = await fetchJson<RunResponse>("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan_id: planId, grant_id: approval.grant_id }),
      });
      setStatusMessage(
        `Run started. grant_id: ${approval.grant_id} · run_id: ${run.run_id} · status: ${run.status}`
      );
      onRunReady?.(run.run_id);
    } catch (requestError) {
      setStatusMessage("");
      setError(requestError instanceof Error ? requestError.message : "Approve failed");
    } finally {
      setIsApproving(false);
      setIsStartingRun(false);
    }
  };

  return (
    <PageSection>
      <PageHeader
        description="Review each generated step before approval and run trigger."
        eyebrow="Approve"
        title="Checklist review before approve and run."
      />
      <Stack gap="sm">
        <TextInput
          onChange={(event) => setPlanId(event.target.value)}
          placeholder="Enter plan_id"
          value={planId}
        />
        <ActionBar>
          <Button onClick={loadPlan} disabled={isLoadingPlan || isApproving || !planId.trim()}>
            {isLoadingPlan ? "Loading..." : "Load Plan"}
          </Button>
          <Button
            onClick={approve}
            disabled={isLoadingPlan || isApproving || isStartingRun || !planId.trim() || !selected.length}
          >
            {isApproving ? "Approving..." : isStartingRun ? "Starting Run..." : "Approve and Run"}
          </Button>
        </ActionBar>
        {error ? (
          <Alert color="red" variant="light">
            {error}
          </Alert>
        ) : null}
        {dependencyWarning ? (
          <Alert color="yellow" variant="light">
            {dependencyWarning}
          </Alert>
        ) : null}
        {plan ? (
          <Stack gap="sm">
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
                <Checkbox
                  checked={selected.includes(step.step_id)}
                  label={`${step.step_id} · ${step.action_type} · ${
                    step.read_or_write === "WRITE" ? "write action" : "read action"
                  }`}
                  onChange={() => toggleStep(step.step_id)}
                />
              </Paper>
            ))}
          </Stack>
        ) : null}
        {statusMessage ? (
          <Text size="sm">approve: {statusMessage}</Text>
        ) : null}
      </Stack>
    </PageSection>
  );
}
