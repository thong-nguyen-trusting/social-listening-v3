import type { ReactNode } from "react";
import { Group } from "@mantine/core";

type ActionBarProps = {
  children: ReactNode;
};

export function ActionBar({ children }: ActionBarProps) {
  return (
    <Group gap="sm" mt="sm">
      {children}
    </Group>
  );
}
