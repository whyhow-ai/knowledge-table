import {
  MantineColor,
  MantineColorsTuple,
  DEFAULT_THEME,
  DefaultMantineColor
} from "@mantine/core";

const extraColors = {
  blueGray: [
    "#f3f3fe",
    "#e4e6ed",
    "#c8cad3",
    "#a9adb9",
    "#9093a4",
    "#808496",
    "#767c91",
    "#656a7e",
    "#585e72",
    "#4a5167"
  ],
  brown: [
    "#f7f3f2",
    "#e7e5e5",
    "#d2c9c6",
    "#bdaaa4",
    "#ab9087",
    "#a17f75",
    "#9d766b",
    "#896459",
    "#7b584e",
    "#6d4b40"
  ],
  tomato: [
    "#fff0e4",
    "#ffe0cf",
    "#fac0a1",
    "#f69e6e",
    "#f28043",
    "#f06d27",
    "#f06418",
    "#d6530c",
    "#bf4906",
    "#a73c00"
  ],
  brightOrange: [
    "#fff8e1",
    "#ffefcc",
    "#ffdd9b",
    "#ffca64",
    "#ffba38",
    "#ffb01b",
    "#ffab09",
    "#e39500",
    "#ca8500",
    "#af7100"
  ],
  brightGreen: [
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
  lightBlue: [
    "#e0fbff",
    "#cbf2ff",
    "#9ae2ff",
    "#64d2ff",
    "#3cc5fe",
    "#23bcfe",
    "#09b8ff",
    "#00a1e4",
    "#0090cd",
    "#007cb5"
  ],
  paleBlue: [
    "#eef3ff",
    "#dce4f5",
    "#b9c7e2",
    "#94a8d0",
    "#748dc1",
    "#5f7cb8",
    "#5474b4",
    "#44639f",
    "#39588f",
    "#2d4b81"
  ],
  paleIndigo: [
    "#eef3ff",
    "#dee2f2",
    "#bdc2de",
    "#98a0ca",
    "#7a84ba",
    "#6672b0",
    "#5c68ac",
    "#4c5897",
    "#424e88",
    "#364379"
  ],
  purple: [
    "#f3edff",
    "#e0d7fa",
    "#beabf0",
    "#9a7ce6",
    "#7c56de",
    "#683dd9",
    "#5f2fd8",
    "#4f23c0",
    "#451eac",
    "#3a1899"
  ]
} satisfies Record<string, MantineColorsTuple>;

export const colors: Record<MantineColor, MantineColorsTuple> = {
  ...DEFAULT_THEME.colors,
  ...extraColors,
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
    "#e6fdee",
    "#d7f5e1",
    "#b1e8c4",
    "#88daa3",
    "#66cf89",
    "#4fc877",
    "#42c46e",
    "#31ad5c",
    "#269a50",
    "#138542"
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

type ExtendedCustomColors = keyof typeof extraColors | DefaultMantineColor;

declare module "@mantine/core" {
  export interface MantineThemeColorsOverride {
    colors: Record<ExtendedCustomColors, MantineColorsTuple>;
  }
}
