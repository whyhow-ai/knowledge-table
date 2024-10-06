import { useMemo } from "react";
import {
  ActionIcon,
  Anchor,
  Badge,
  Button,
  Checkbox,
  createTheme,
  DEFAULT_THEME,
  Group,
  List,
  Loader,
  MantineThemeOverride,
  mergeMantineTheme,
  Popover,
  ScrollArea,
  Text,
  Tooltip
} from "@mantine/core";
import { useStore } from "./store";

export function useTheme() {
  const colorScheme = useStore(store => store.colorScheme);
  return useMemo(() => getTheme(colorScheme), [colorScheme]);
}

const getTheme = (colorScheme: "light" | "dark") =>
  mergeMantineTheme(
    DEFAULT_THEME,
    createTheme({
      fontFamily: '"Inter", sans-serif',
      defaultRadius: "md",
      primaryColor: "blue",
      primaryShade: { light: 4, dark: 8 },
      colors,
      components: {
        ActionIcon: ActionIcon.extend({
          defaultProps: {
            variant: "subtle",
            color: colorScheme === "dark" ? "gray" : "dark"
          }
        }),
        Anchor: Anchor.extend({
          defaultProps: {
            size: "sm",
            underline: "never"
          }
        }),
        Badge: Badge.extend({
          defaultProps: {
            size: "sm",
            variant: "light"
          }
        }),
        Button: Button.extend({
          defaultProps: {
            variant: "subtle",
            size: "compact-sm",
            color: colorScheme === "dark" ? "gray" : "dark"
          }
        }),
        Checkbox: Checkbox.extend({
          defaultProps: {
            radius: "sm"
          }
        }),
        Group: Group.extend({
          defaultProps: {
            gap: "sm"
          }
        }),
        List: List.extend({
          defaultProps: {
            size: "sm",
            listStyleType: "none"
          }
        }),
        Loader: Loader.extend({
          defaultProps: {
            size: "sm",
            type: "dots"
          }
        }),
        Popover: Popover.extend({
          defaultProps: {
            shadow: "sm"
          }
        }),
        ScrollArea: ScrollArea.extend({
          styles: {
            scrollbar: {
              zIndex: 5
            }
          }
        }),
        Text: Text.extend({
          defaultProps: {
            size: "sm"
          }
        }),
        Tooltip: Tooltip.extend({
          defaultProps: {
            withArrow: true
          }
        })
      }
    })
  );

const colors: MantineThemeOverride["colors"] = {
  blue: [
    "#ebf0ff",
    "#d2ddfa",
    "#a1b8f7",
    "#6c90f6",
    "#456ff5",
    "#2f5af6",
    "#254ff7",
    "#1b41dc",
    "#133ac5",
    "#0031ad"
  ],
  red: [
    "#ffe9f0",
    "#fed3db",
    "#f7a4b4",
    "#f1728b",
    "#ec4869",
    "#ea2f53",
    "#ea2147",
    "#d01339",
    "#bb0a31",
    "#a40029"
  ],
  green: [
    "#effee7",
    "#e0f8d4",
    "#c2efab",
    "#a2e67e",
    "#87de57",
    "#75d940",
    "#6bd731",
    "#59be23",
    "#4da91b",
    "#3d920c"
  ],
  dark: [
    "#c0c5d2",
    "#acb3c4",
    "#6d7997",
    "#57617b",
    "#373d4d",
    "#313745",
    "#262b36",
    "#1e212a",
    "#1a1d24",
    "#111317"
  ]
};
