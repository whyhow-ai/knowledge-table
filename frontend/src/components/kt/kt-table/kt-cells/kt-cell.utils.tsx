import { HTMLAttributes, ReactNode, RefObject, useEffect, useRef } from "react";
import { Uncertain } from "@silevis/reactgrid";
import { Text, Badge, Box } from "@mantine/core";
import { isArray, isBoolean } from "lodash-es";
import { KtCell } from "./kt-cell";
import { CellValue } from "@config/store";
import { niceTry } from "@utils/functions";

// Utility

export function isKtCell(cell: Uncertain<KtCell>): cell is KtCell {
  return Boolean(cell.type === "kt-cell" && cell.column && cell.row);
}

export function formatCell(cell?: CellValue): ReactNode {
  if (cell === undefined) {
    return null;
  } else if (cell === null) {
    return <Text c="dimmed">Not found</Text>;
  } else if (isBoolean(cell)) {
    return <Badge>{String(cell)}</Badge>;
  } else {
    return (
      <Text lineClamp={2}>
        {isArray(cell) ? cell.join(", ") : String(cell)}
      </Text>
    );
  }
}

// Editor wrapper

type EditorWrapperProps = {
  defaultValue: CellValue;
  onChange: (value: CellValue, commit?: boolean) => void;
  children: (
    inputProps: InputProps,
    handleChange: (value: CellValue) => void
  ) => ReactNode;
};

type InputProps = Pick<
  HTMLAttributes<HTMLElement>,
  "onCopy" | "onCut" | "onPaste"
> & { ref: RefObject<any> };

export function EditorWrapper({
  defaultValue,
  onChange,
  children
}: EditorWrapperProps) {
  const inputRef = useRef<any>(null);
  const escapedPressed = useRef(false);
  const lastChange = useRef(defaultValue);

  const handleChange = (value: CellValue) => {
    lastChange.current = value;
    onChange(value);
  };

  const inputProps: InputProps = {
    ref: inputRef,
    onCopy: e => e.stopPropagation(),
    onCut: e => e.stopPropagation(),
    onPaste: e => e.stopPropagation()
  };

  useEffect(
    () =>
      niceTry(() => {
        const input = inputRef.current;
        if (!input) return;
        input.focus();
        input.setSelectionRange(input.value.length, input.value.length);
      }),
    []
  );

  return (
    <Box
      w="100%"
      mih="100%"
      tabIndex={0}
      onPointerDown={e => e.stopPropagation()}
      onBlur={() => {
        onChange(lastChange.current, !escapedPressed.current);
        escapedPressed.current = false;
      }}
      onKeyDown={e => {
        if (e.key === "Escape") {
          escapedPressed.current = true;
        }
        if (!["Escape", "Enter"].includes(e.key)) {
          e.stopPropagation();
        }
      }}
    >
      {children(inputProps, handleChange)}
    </Box>
  );
}
