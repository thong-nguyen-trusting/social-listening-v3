import {
  ActionIcon,
  Button,
  Container,
  Group,
  Text,
  useComputedColorScheme,
  useMantineColorScheme,
} from "@mantine/core";
import { apiUrl } from "../../lib/api";

type AppHeaderProps = {
  displayName: string;
  currentPhaseName?: string | null;
  releaseNotesHref?: string | null;
};

const links = [
  { label: "Browser", href: apiUrl("/api/browser/status") },
  { label: "Health", href: apiUrl("/api/health/status") },
  { label: "Sessions", href: apiUrl("/api/sessions") },
  { label: "Runs", href: apiUrl("/api/runs") },
];

export function AppHeader({ displayName, currentPhaseName, releaseNotesHref }: AppHeaderProps) {
  const { setColorScheme } = useMantineColorScheme();
  const colorScheme = useComputedColorScheme("light", {
    getInitialValueInEffect: true,
  });
  const nextColorScheme = colorScheme === "dark" ? "light" : "dark";

  return (
    <Container
      h="100%"
      size="lg"
      style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}
    >
      <Group gap="xs" wrap="nowrap">
        <Button component="a" href="#/" px={0} styles={{ root: { height: "auto" } }} variant="subtle">
          <div>
            <Text fw={700} size="sm">
              {displayName}
            </Text>
            {currentPhaseName ? (
              <Text c="dimmed" size="xs">
                {currentPhaseName}
              </Text>
            ) : null}
          </div>
        </Button>
      </Group>

      <Group gap="xs" wrap="wrap" justify="flex-end">
        {releaseNotesHref ? (
          <Button component="a" href={releaseNotesHref} size="compact-sm" variant="light">
            Release Notes
          </Button>
        ) : null}
        {links.map((link) => (
          <Button
            component="a"
            href={link.href}
            key={link.href}
            rel="noreferrer"
            size="compact-sm"
            target="_blank"
            variant="subtle"
          >
            {link.label}
          </Button>
        ))}
        <ActionIcon
          aria-label={`Switch to ${nextColorScheme} mode`}
          onClick={() => setColorScheme(nextColorScheme)}
          size="lg"
          variant="default"
        >
          {colorScheme === "dark" ? "L" : "D"}
        </ActionIcon>
      </Group>
    </Container>
  );
}
