import { createTheme } from "@mantine/core";
import {
  brandColors,
  dangerColors,
  fontFamily,
  fontFamilyMonospace,
  infoColors,
  successColors,
  warningColors,
} from "./tokens";

export const appTheme = createTheme({
  primaryColor: "brand",
  colors: {
    brand: [...brandColors],
    green: [...successColors],
    yellow: [...warningColors],
    red: [...dangerColors],
    blue: [...infoColors],
  },
  spacing: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "1rem",
    lg: "1.5rem",
    xl: "2rem",
  },
  radius: {
    xs: "0.25rem",
    sm: "0.5rem",
    md: "0.75rem",
    lg: "1rem",
    xl: "1.5rem",
  },
  shadows: {
    xs: "0 1px 2px rgba(15, 23, 42, 0.08)",
    sm: "0 10px 24px rgba(15, 23, 42, 0.08)",
    md: "0 18px 40px rgba(15, 23, 42, 0.12)",
    lg: "0 28px 56px rgba(15, 23, 42, 0.18)",
  },
  fontFamily,
  fontFamilyMonospace,
  headings: {
    fontFamily,
    sizes: {
      h1: { fontSize: "2rem", lineHeight: "1.1", fontWeight: "700" },
      h2: { fontSize: "1.5rem", lineHeight: "1.15", fontWeight: "700" },
      h3: { fontSize: "1.25rem", lineHeight: "1.2", fontWeight: "700" },
      h4: { fontSize: "1.125rem", lineHeight: "1.25", fontWeight: "700" },
      h5: { fontSize: "1rem", lineHeight: "1.3", fontWeight: "700" },
      h6: { fontSize: "0.875rem", lineHeight: "1.35", fontWeight: "700" },
    },
  },
  components: {
    Paper: {
      defaultProps: {
        radius: "md",
        shadow: "xs",
      },
    },
    Button: {
      defaultProps: {
        radius: "md",
      },
    },
    TextInput: {
      defaultProps: {
        radius: "sm",
      },
    },
    Textarea: {
      defaultProps: {
        radius: "sm",
      },
    },
    Badge: {
      defaultProps: {
        radius: "xl",
      },
    },
    Alert: {
      defaultProps: {
        radius: "md",
      },
    },
    Card: {
      defaultProps: {
        radius: "lg",
      },
    },
  },
});
