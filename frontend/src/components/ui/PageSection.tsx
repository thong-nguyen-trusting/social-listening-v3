import type { ReactNode } from "react";
import { Paper, Stack, useComputedColorScheme } from "@mantine/core";
import { semanticColors } from "../../theme/tokens";

type PageSectionProps = {
  children: ReactNode;
  p?: "xs" | "sm" | "md" | "lg" | "xl";
  withBorder?: boolean;
};

export function PageSection({
  children,
  p = "lg",
  withBorder = true,
}: PageSectionProps) {
  const colorScheme = useComputedColorScheme("light", {
    getInitialValueInEffect: true,
  });
  const palette = colorScheme === "dark" ? semanticColors.dark : semanticColors.light;

  return (
    <Paper
      bg={palette.panel}
      p={p}
      radius="lg"
      shadow="xs"
      style={{ minHeight: "100%" }}
      withBorder={withBorder}
    >
      <Stack gap="md">{children}</Stack>
    </Paper>
  );
}
