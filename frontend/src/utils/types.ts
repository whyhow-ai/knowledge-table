export type Falsy = null | undefined | false | "" | 0 | 0n;

export type Pack<T> = T | Falsy | Array<Pack<T>>;

export type StateHandlers<K extends string, T> = {
  [k in K]?: T;
} & {
  [k in `default${Capitalize<K>}`]?: T;
} & {
  [k in `on${Capitalize<K>}Change`]?: (value: T) => void;
};
