import { compact, flattenDeep, isArray, isFunction, noop } from "lodash-es";
import { Pack } from "./types";

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
