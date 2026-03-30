import {
  Alert,
  Badge,
  Button,
  List,
  Paper,
  SegmentedControl,
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
import { fetchJson, withQuery } from "../lib/api";

type Theme = {
  theme_id: string;
  label: string;
  dominant_sentiment: string;
  post_count: number;
  sample_quotes: string[];
};

type ThemeResponse = {
  run_id: string;
  audience_filter: AudienceFilter;
  taxonomy_version: string;
  posts_crawled: number;
  posts_included: number;
  posts_excluded: number;
  excluded_by_label_count: number;
  excluded_breakdown: Record<string, number>;
  warning: string | null;
  themes: Theme[];
};

type AudienceFilter = "end_user_only" | "include_seller" | "include_brand";

const labelMap: Record<string, string> = {
  pain_point: "Van de / diem dau",
  positive_feedback: "Phan hoi tich cuc",
  question: "Cau hoi",
  comparison: "So sanh",
  other: "Khac",
};

const audienceOptions = [
  { label: "End-user only", value: "end_user_only" },
  { label: "Include seller", value: "include_seller" },
  { label: "Include brand", value: "include_brand" },
];

type ThemesPageProps = {
  initialRunId?: string;
};

export function ThemesPage({ initialRunId = "" }: ThemesPageProps) {
  const [runId, setRunId] = useState("");
  const [audienceFilter, setAudienceFilter] = useState<AudienceFilter>("end_user_only");
  const [analysis, setAnalysis] = useState<ThemeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  useEffect(() => {
    if (!initialRunId || initialRunId === runId) {
      return;
    }
    setRunId(initialRunId);
    setAnalysis(null);
    setError("");
    setStatusMessage(`Run received from monitor: ${initialRunId}`);
  }, [initialRunId]);

  const loadThemes = async (targetFilter = audienceFilter) => {
    const normalizedRunId = runId.trim();
    if (!normalizedRunId) return;
    setIsLoading(true);
    setError("");
    setStatusMessage(`Loading themes for ${normalizedRunId} with ${targetFilter}...`);
    try {
      const payload = await fetchJson<ThemeResponse>(
        withQuery(`/api/runs/${normalizedRunId}/themes`, { audience_filter: targetFilter })
      );
      setAnalysis(payload);
      setStatusMessage(`Themes loaded for ${normalizedRunId}. ${payload.themes.length} groups ready.`);
    } catch (requestError) {
      setAnalysis(null);
      setStatusMessage("");
      setError(requestError instanceof Error ? requestError.message : "Load themes failed");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (nextFilter: AudienceFilter) => {
    setAudienceFilter(nextFilter);
    if (runId.trim()) {
      void loadThemes(nextFilter);
    }
  };

  return (
    <PageSection>
      <PageHeader
        description="Inspect filtered themes, audience presets, sentiment, and sample quotes."
        eyebrow="Themes"
        title="Theme groups with sentiment and sample quotes."
      />
      <Stack gap="sm">
        <TextInput
          onChange={(event) => setRunId(event.target.value)}
          placeholder="Enter run_id"
          value={runId}
        />
        <SegmentedControl
          data={audienceOptions}
          onChange={(value) => handleFilterChange(value as AudienceFilter)}
          value={audienceFilter}
        />
        <ActionBar>
          <Button onClick={() => void loadThemes()} disabled={!runId.trim() || isLoading}>
            {isLoading ? "Loading..." : "Load Themes"}
          </Button>
        </ActionBar>
        {error ? (
          <Alert color="red" variant="light">
            {error}
          </Alert>
        ) : null}
        {runId ? <KeyValueRow label="run_id" mono value={runId} /> : null}
        <KeyValueRow label="audience filter" value={audienceFilter} />
        {statusMessage ? <Text size="sm">themes: {statusMessage}</Text> : null}
        {analysis ? (
          <Stack gap="sm">
            <KeyValueRow label="taxonomy" value={analysis.taxonomy_version} />
            <KeyValueRow
              label="included"
              value={`${analysis.posts_included}/${analysis.posts_crawled}`}
            />
            <KeyValueRow
              label="excluded by label"
              value={`${analysis.excluded_by_label_count} hidden total ${analysis.posts_excluded}`}
            />
            {analysis.warning ? (
              <Alert color="yellow" variant="light">
                {analysis.warning}
              </Alert>
            ) : null}
            <Stack gap="xs">
              {Object.entries(analysis.excluded_breakdown).map(([reason, count]) => (
                <Badge key={reason} variant="light">
                  {reason}: {count}
                </Badge>
              ))}
            </Stack>
            {analysis.themes.map((theme) => (
              <Paper key={theme.theme_id} p="sm" radius="md" withBorder>
                <Stack gap="sm">
                  <Text fw={700} size="sm">
                    {labelMap[theme.label] ?? theme.label}
                  </Text>
                  <StatusBadge label={`Sentiment ${theme.dominant_sentiment}`} status={theme.dominant_sentiment} />
                  <KeyValueRow label="post count" value={theme.post_count} />
                  <List size="sm" spacing="xs">
                    {theme.sample_quotes.map((quote) => (
                      <List.Item key={quote}>{quote}</List.Item>
                    ))}
                  </List>
                </Stack>
              </Paper>
            ))}
          </Stack>
        ) : null}
      </Stack>
    </PageSection>
  );
}
