import { useLayoutEffect, useRef } from "react";

export function useEventCallback<F extends (...args: any[]) => any>(
  callback: F
) {
  const ref = useRef(callback);
  useLayoutEffect(() => {
    ref.current = callback;
  }, [callback]);
  const { current: eventCallback } = useRef(((...args) =>
    ref.current(...args)) as F);
  return eventCallback;
}
