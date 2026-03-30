import type { ReactNode } from "react";
import {
  AppShell,
  Container,
  useComputedColorScheme,
} from "@mantine/core";
import { semanticColors } from "../../theme/tokens";
import { AppHeader } from "./AppHeader";

type AppLayoutProps = {
  children: ReactNode;
  displayName: string;
  currentPhaseName?: string | null;
  releaseNotesHref?: string | null;
};

export function AppLayout({
  children,
  displayName,
  currentPhaseName,
  releaseNotesHref,
}: AppLayoutProps) {
  const colorScheme = useComputedColorScheme("light", {
    getInitialValueInEffect: true,
  });
  const palette = colorScheme === "dark" ? semanticColors.dark : semanticColors.light;

  return (
    <AppShell
      header={{ height: 60 }}
      padding="md"
      styles={{
        header: {
          backgroundColor: palette.panel,
          borderColor: palette.border,
        },
        main: {
          backgroundColor: palette.app,
          color: palette.textPrimary,
          minHeight: "100vh",
        },
      }}
    >
      <AppShell.Header>
        <AppHeader
          currentPhaseName={currentPhaseName}
          displayName={displayName}
          releaseNotesHref={releaseNotesHref}
        />
      </AppShell.Header>
      <AppShell.Main>
        <Container py="lg" size="lg">
          {children}
        </Container>
      </AppShell.Main>
    </AppShell>
  );
}
