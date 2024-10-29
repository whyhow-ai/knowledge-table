import { useCallback, useLayoutEffect, useMemo, useState } from "react";
import { eq } from "lodash-es";

export function useDerivedState<T>(
  value: T,
  comparator: (value: T, state: T) => boolean = eq
) {
  const [state, set] = useState(value);
  const reset = useCallback(() => set(value), [value]);

  const dirty = useMemo(
    () => !comparator(value, state),
    [value, state, comparator]
  );

  useLayoutEffect(() => {
    dirty && reset();
  }, [value]);

  return [state, { set, dirty, reset }] as const;
}
