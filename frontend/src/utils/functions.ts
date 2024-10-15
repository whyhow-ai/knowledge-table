import { DEFAULT_THEME, isLightColor } from "@mantine/core";
import {
  compact,
  defer,
  flattenDeep,
  isArray,
  isFunction,
  isString,
  noop,
  omit,
  times,
  values
} from "lodash-es";
import { Pack } from "./types";
import { colors } from "@config/theme";

export function pack<T>(...args: Pack<T>[]): T[] {
  return compact(flattenDeep(args));
}

export function wait(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function cn(...classes: Pack<string>[]) {
  return pack(...classes)
    .map(c => (c.startsWith(".") ? c.substring(1) : c))
    .join(" ");
}

export function stopPropagation<
  E extends { stopPropagation(): void },
  R extends any[]
>(handler: (event: E, ...rest: R) => void = noop) {
  return (event: E, ...rest: R) => {
    event.stopPropagation();
    handler(event, ...rest);
  };
}

export function plur(word: string, count: number | any[]) {
  const plural = (isArray(count) ? count.length : count) !== 1;
  if (!plural) return word;
  if (word === "is") return "are";
  if (word.endsWith("sis")) return `${word.substring(0, word.length - 3)}ses`;
  if (word.endsWith("y")) return `${word.substring(0, word.length - 1)}ies`;
  return `${word}s`;
}

export function where<T extends object>(
  array: T[],
  predicate: (item: T) => boolean,
  change: Partial<T> | ((item: T) => Partial<T>)
) {
  const changeFn = isFunction(change) ? change : () => change;
  return array.map(item => {
    if (!predicate(item)) return item;
    return { ...item, ...changeFn(item) };
  });
}

// download

export function download(
  filename: string,
  url: string | Blob | { mimeType: string; content: string }
) {
  let wasBlob = false;
  if (url instanceof Blob) {
    wasBlob = true;
    url = URL.createObjectURL(url);
  } else if (!isString(url)) {
    url = `data:${url.mimeType};charset=utf-8,${encodeURIComponent(
      url.content
    )}`;
  }
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  defer(() => {
    document.body.removeChild(a);
    wasBlob && URL.revokeObjectURL(url);
  });
}

// entityColor

const entityColorCache = new Map<string, { fill: string; text: string }>();

const palette = values(omit(colors, "dark")).flatMap(colors => [
  colors[2],
  colors[4]
]);

export function entityColor(str: string) {
  const cached = entityColorCache.get(str);
  if (cached !== undefined) {
    return cached;
  }
  const hash = Math.abs(
    [...str].reduce((acc, char) => char.charCodeAt(0) + ((acc << 5) - acc), 0)
  );
  const value = times(3).reduce((acc, i) => {
    return (acc + (hash >> (i * 8))) & 0xff;
  }, 0);
  const color = palette[value % palette.length];
  const colors = {
    fill: color,
    text: isLightColor(color) ? DEFAULT_THEME.black : DEFAULT_THEME.white
  };
  entityColorCache.set(str, colors);
  return colors;
}
