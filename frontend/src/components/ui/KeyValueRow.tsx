import type { ReactNode } from "react";
import { Group, Text } from "@mantine/core";

type KeyValueRowProps = {
  label: string;
  value: ReactNode;
  mono?: boolean;
};

export function KeyValueRow({ label, value, mono = false }: KeyValueRowProps) {
  return (
    <Group gap="xs" wrap="wrap">
      <Text c="dimmed" size="sm">
        {label}:
      </Text>
      <Text ff={mono ? "monospace" : undefined} size="sm">
        {value}
      </Text>
    </Group>
  );
}
