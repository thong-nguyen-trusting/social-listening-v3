import type { ReactNode } from "react";
import {
  MantineProvider,
  localStorageColorSchemeManager,
} from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { appTheme } from "../../theme";

const colorSchemeManager = localStorageColorSchemeManager({
  key: "social-listening-v3-color-scheme",
});

type ThemeProviderProps = {
  children: ReactNode;
};

export function ThemeProvider({ children }: ThemeProviderProps) {
  return (
    <MantineProvider
      colorSchemeManager={colorSchemeManager}
      defaultColorScheme="auto"
      theme={appTheme}
    >
      <Notifications position="top-right" />
      {children}
    </MantineProvider>
  );
}
