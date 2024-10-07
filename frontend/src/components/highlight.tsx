import React, { HTMLAttributes } from "react";
import {
  Text,
  Mark,
  TextProps,
  Tooltip,
  MantineColor,
  isLightColor,
  useMantineTheme,
  parseThemeColor
} from "@mantine/core";
import { escapeRegExp, isEmpty } from "lodash-es";
import { Wrap } from "./wrap";
import { useStore } from "@config/store";

type Props = TextProps &
  HTMLAttributes<HTMLParagraphElement> & {
    children: string;
    highlights?: Array<{
      color: MantineColor | string;
      words: string[];
      description?: React.ReactNode;
    }>;
  };

export function Highlight({ children, highlights, ...props }: Props) {
  const theme = useMantineTheme();
  const colorScheme = useStore(store => store.colorScheme);
  const wordMap = new Map(
    highlights?.flatMap(h => h.words.map(word => [word.toLowerCase(), h]))
  );
  const escapedWords = [...wordMap.keys()].map(escapeRegExp);
  const regex = new RegExp(`\\b(${escapedWords.join("|")})\\b`, "gi");

  const getHighlightedText = (text: string) => {
    const parts = text.split(regex);
    return parts.map((part, index) => {
      const highlight = wordMap.get(part.toLowerCase());
      if (!highlight) {
        return part;
      } else {
        const textColor = isLightColor(
          parseThemeColor({ color: highlight.color, theme }).value
        )
          ? theme.black
          : colorScheme === "light"
          ? theme.white
          : theme.colors.dark[0];
        return (
          <Wrap
            key={index}
            with={
              highlight.description &&
              (node => <Tooltip label={highlight.description}>{node}</Tooltip>)
            }
          >
            <Mark color={highlight.color} c={textColor}>
              {part}
            </Mark>
          </Wrap>
        );
      }
    });
  };

  return (
    <Text {...props}>
      {isEmpty(escapedWords) ? children : getHighlightedText(children)}
    </Text>
  );
}
