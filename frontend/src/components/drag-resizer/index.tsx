import { useEffect, useMemo, useState, type MouseEvent } from "react";
import { createPortal } from "react-dom";
import { Box } from "@mantine/core";
import { cn } from "@utils/functions";
import classes from "./index.module.css";

interface Props {
  position?: "top" | "right" | "bottom" | "left";
  value: number;
  onChange: (width: number) => void;
}

export function DragResizer({ position = "right", value, onChange }: Props) {
  const [dragging, setDragging] = useState(false);
  const [startSize, setStartSize] = useState(0);
  const [startCoord, setStartCoord] = useState(0);

  const { isVertical, isBefore } = useMemo(
    () => ({
      isVertical: ["top", "bottom"].includes(position),
      isBefore: ["top", "left"].includes(position)
    }),
    [position]
  );

  const onMouseDown = (e: MouseEvent) => {
    if (e.button !== 0) return;
    setDragging(true);
    setStartSize(value);
    setStartCoord(isVertical ? e.clientY : e.clientX);
    window.getSelection()?.removeAllRanges();
  };

  const onMouseMove = (e: MouseEvent) => {
    if (e.buttons !== 1) {
      setDragging(false);
      return;
    }
    const delta =
      ((isVertical ? e.clientY : e.clientX) - startCoord) * (isBefore ? -1 : 1);
    onChange(startSize + delta);
  };

  const onMouseUp = () => {
    setDragging(false);
  };

  useEffect(() => {
    if (dragging) {
      document.body.style.userSelect = "none";
      return () => {
        document.body.style.userSelect = "";
      };
    }
  }, [dragging]);

  return (
    <>
      <Box
        onMouseDown={onMouseDown}
        className={cn(
          classes.handle,
          classes[position],
          dragging && classes.active
        )}
      />
      {dragging &&
        createPortal(
          <Box
            onMouseMove={onMouseMove}
            onMouseUp={onMouseUp}
            className={cn(
              classes.overlay,
              isVertical ? classes.vertical : classes.horizontal
            )}
          />,
          document.body
        )}
    </>
  );
}
