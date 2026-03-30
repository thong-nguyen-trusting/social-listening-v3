import { SimpleGrid, Stack } from "@mantine/core";
import { useEffect, useState } from "react";
import { AppLayout } from "./app/shell/AppLayout";
import { HealthBadge } from "./components/HealthBadge";
import { fetchJson } from "./lib/api";
import { readHashRoute, type AppRoute, type RuntimeMetadata } from "./lib/runtime";
import { ApprovePage } from "./pages/ApprovePage";
import { KeywordPage } from "./pages/KeywordPage";
import { MonitorPage } from "./pages/MonitorPage";
import { PlanPage } from "./pages/PlanPage";
import { ReleaseNotesPage } from "./pages/ReleaseNotesPage";
import { SetupPage } from "./pages/SetupPage";
import { ThemesPage } from "./pages/ThemesPage";

export default function App() {
  const [activeContextId, setActiveContextId] = useState("");
  const [activePlanId, setActivePlanId] = useState("");
  const [activeRunId, setActiveRunId] = useState("");
  const [route, setRoute] = useState<AppRoute>(() => readHashRoute());
  const [runtimeMetadata, setRuntimeMetadata] = useState<RuntimeMetadata | null>(null);

  const handleContextReady = (contextId: string) => {
    setActiveContextId(contextId);
    setActivePlanId("");
    setActiveRunId("");
  };

  const handlePlanReady = (planId: string) => {
    setActivePlanId(planId);
    setActiveRunId("");
  };

  const handleRunReady = (runId: string) => {
    setActiveRunId(runId);
  };

  useEffect(() => {
    const handleHashChange = () => setRoute(readHashRoute());
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadRuntimeMetadata() {
      try {
        const payload = await fetchJson<RuntimeMetadata>("/api/runtime/metadata");
        if (!cancelled) {
          setRuntimeMetadata(payload);
        }
      } catch {
        if (!cancelled) {
          setRuntimeMetadata(null);
        }
      }
    }

    void loadRuntimeMetadata();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const displayName = runtimeMetadata?.display_name ?? "Social Listening v3";
    document.title = route.name === "release-notes" ? `${displayName} Release Notes` : displayName;
  }, [route.name, runtimeMetadata?.display_name]);

  return (
    <AppLayout
      currentPhaseName={runtimeMetadata?.current_phase_name}
      displayName={runtimeMetadata?.display_name ?? "Social Listening v3"}
      releaseNotesHref={runtimeMetadata?.release_notes_href}
    >
      {route.name === "release-notes" ? (
        <ReleaseNotesPage phaseId={route.phaseId ?? runtimeMetadata?.current_phase ?? undefined} />
      ) : (
        <Stack gap="lg">
          <SimpleGrid cols={{ base: 1, sm: 2 }}>
            <SetupPage />
            <HealthBadge />
          </SimpleGrid>

          <SimpleGrid cols={{ base: 1, sm: 2 }}>
            <KeywordPage onContextReady={handleContextReady} />
            <PlanPage initialContextId={activeContextId} onPlanReady={handlePlanReady} />
            <ApprovePage initialPlanId={activePlanId} onRunReady={handleRunReady} />
            <MonitorPage initialRunId={activeRunId} onRunSelected={handleRunReady} />
            <ThemesPage initialRunId={activeRunId} />
          </SimpleGrid>
        </Stack>
      )}
    </AppLayout>
  );
}
