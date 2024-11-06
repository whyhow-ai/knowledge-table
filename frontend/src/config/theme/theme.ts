import { useMemo } from "react";
import {
  ActionIcon,
  Anchor,
  Badge,
  Blockquote,
  Button,
  Checkbox,
  ColorSwatch,
  createTheme,
  DEFAULT_THEME,
  Group,
  List,
  Loader,
  mergeMantineTheme,
  Modal,
  Popover,
  ScrollArea,
  Text,
  Tooltip
} from "@mantine/core";
import { colors } from "./colors";
import { useStore } from "../store";

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
        Blockquote: Blockquote.extend({
          defaultProps: {
            fz: "sm"
          },
          styles: {
            root: {
              padding: `${DEFAULT_THEME.spacing.xs} ${DEFAULT_THEME.spacing.md}`
            }
          }
        }),
        Button: Button.extend({
          defaultProps: {
            variant: "subtle",
            color: colorScheme === "dark" ? "gray" : "dark"
          }
        }),
        Checkbox: Checkbox.extend({
          defaultProps: {
            radius: "sm"
          }
        }),
        ColorSwatch: ColorSwatch.extend({
          defaultProps: {
            withShadow: false
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
        Modal: Modal.extend({
          defaultProps: {
            centered: true
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
