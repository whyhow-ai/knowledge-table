import { CSSProperties, ReactElement } from "react";
import { Box, Popover, ScrollArea } from "@mantine/core";
import { compact } from "lodash-es";
import {
  DataGridDropdown,
  DataGridDrag,
  DataGridCell,
  DataGridCellWithoutKey
} from "./data-grid.types";
import { Wrap } from "@components";
import classes from "./data-grid.module.css";

export function gridStyle(
  columns: DataGridCell[],
  rows: DataGridCell[],
  extraColumn?: DataGridCellWithoutKey,
  extraRow?: DataGridCellWithoutKey
) {
  return {
    gridTemplateColumns: compact([
      rows[0] ?? extraRow ?? {},
      ...columns,
      extraColumn
    ])
      .map(column => `${column.width ?? 100}px`)
      .join(" ")
  };
}

export function cellStyle(
  x: number,
  y: number,
  spanX = 1,
  spanY = 1
): CSSProperties {
  return {
    gridColumn: `${x + 2} / span ${spanX}`,
    gridRow: `${y + 2} / span ${spanY}`
  };
}

export function popover(dropdown?: DataGridDropdown, node?: ReactElement) {
  return !dropdown ? (
    node
  ) : (
    <Popover
      key={node?.key}
      offset={0}
      width="target"
      position="bottom-start"
      transitionProps={{ transition: "scale-y" }}
    >
      <Popover.Target>{node}</Popover.Target>
      <Popover.Dropdown className={classes.dropdown}>
        <Wrap
          with={
            dropdown.scrollable &&
            (node => (
              <ScrollArea.Autosize mah={500}>{node}</ScrollArea.Autosize>
            ))
          }
        >
          <Box p="sm">{dropdown.content}</Box>
        </Wrap>
      </Popover.Dropdown>
    </Popover>
  );
}

export function getCellsInRange(
  start: string,
  end: string,
  columns: DataGridCell[],
  rows: DataGridCell[],
  cellKeyDelimiter: string
) {
  const [startRow, startCol] = start.split(cellKeyDelimiter);
  const [endRow, endCol] = end.split(cellKeyDelimiter);

  const columnIndex = new Map(columns.map((column, i) => [column.key, i]));
  const rowIndex = new Map(rows.map((row, i) => [row.key, i]));

  let startX = columnIndex.get(startCol) ?? 0;
  let startY = rowIndex.get(startRow) ?? 0;
  let endX = columnIndex.get(endCol) ?? 0;
  let endY = rowIndex.get(endRow) ?? 0;

  if (startX > endX) [startX, endX] = [endX, startX];
  if (startY > endY) [startY, endY] = [endY, startY];

  const selection = new Set<string>();
  for (let y = startY; y <= endY; y++) {
    for (let x = startX; x <= endX; x++) {
      selection.add(`${rows[y]?.key}${cellKeyDelimiter}${columns[x]?.key}`);
    }
  }
  return selection;
}

export function getDragSelection(
  drag: DataGridDrag,
  columns: DataGridCell[],
  rows: DataGridCell[],
  cellKeyDelimiter: string
) {
  const selection = getCellsInRange(
    drag.start,
    drag.end,
    columns,
    rows,
    cellKeyDelimiter
  );
  if (drag.ctrl) {
    for (const key of drag.initialSelection) {
      if (selection.has(key)) {
        selection.delete(key);
      } else {
        selection.add(key);
      }
    }
  }
  return [...selection];
}
