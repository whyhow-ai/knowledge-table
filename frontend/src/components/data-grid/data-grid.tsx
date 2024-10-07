import { useMemo, useState, MouseEvent, useEffect } from "react";
import { Box, BoxProps } from "@mantine/core";
import { useHotkeys, useUncontrolled } from "@mantine/hooks";
import { times } from "lodash-es";
import {
  cellStyle,
  getDragSelection,
  gridStyle,
  popover
} from "./data-grid.utils";
import {
  DataGridCell,
  DataGridCellWithoutKey,
  DataGridDrag
} from "./data-grid.types";
import { cn } from "@utils/functions";
import classes from "./data-grid.module.css";

export interface DataGridProps extends BoxProps {
  columns: DataGridCell[];
  rows: DataGridCell[];
  cells: DataGridCell[];
  extraColumn?: DataGridCellWithoutKey;
  extraRow?: DataGridCellWithoutKey;
  cellKeyDelimiter?: string;
  defaultCell?: (key: string) => DataGridCellWithoutKey;
  selection?: string[];
  onSelectionChange?: (selection: string[]) => void;
}

export const DataGrid = ({
  columns,
  rows,
  cells,
  extraColumn,
  extraRow,
  cellKeyDelimiter = "-",
  defaultCell,
  selection: selection_,
  onSelectionChange,
  ...props
}: DataGridProps) => {
  const [drag, setDrag] = useState<null | DataGridDrag>(null);
  const [selection, setSelection] = useUncontrolled({
    value: selection_,
    defaultValue: [],
    onChange: onSelectionChange
  });
  const selectionSet = useMemo(() => new Set(selection), [selection]);

  useHotkeys([
    [
      "Escape",
      () => {
        setSelection([]);
        setDrag(null);
      }
    ]
  ]);

  const cellMap = useMemo(
    () => new Map(cells.map(cell => [cell.key, cell])),
    [cells]
  );

  const handleColumnMouseDown = (key: string) => (e: MouseEvent) => {
    if (e.buttons === 1) {
      setSelection(rows.map(row => `${row.key}${cellKeyDelimiter}${key}`));
    }
  };

  const handleRowMouseDown = (key: string) => (e: MouseEvent) => {
    if (e.buttons === 1) {
      setSelection(
        columns.map(column => `${key}${cellKeyDelimiter}${column.key}`)
      );
    }
  };

  const handleCellMouseDown = (key: string) => (e: MouseEvent) => {
    if (e.buttons === 1) {
      setDrag({
        start: key,
        end: key,
        ctrl: e.ctrlKey,
        initialSelection: selection
      });
    }
  };

  const handleCellMouseEnter = (key: string) => (e: MouseEvent) => {
    if (e.buttons === 1 && drag) {
      setDrag({ ...drag, end: key, ctrl: e.ctrlKey });
    }
  };

  useEffect(() => {
    drag &&
      setSelection(getDragSelection(drag, columns, rows, cellKeyDelimiter));
  }, [drag]);

  return (
    <Box
      {...props}
      style={{ ...gridStyle(columns, rows, extraColumn), ...props.style }}
      className={cn(classes.dataGrid, props.className)}
    >
      <Box
        style={cellStyle(-1, -1)}
        className={cn(classes.cell, classes.header, classes.origin)}
      />

      {columns.map((column, index) =>
        popover(
          column.dropdown,
          <Box
            key={column.key}
            onClick={column.onClick}
            onMouseDown={handleColumnMouseDown(column.key)}
            style={cellStyle(index, -1)}
            className={cn(classes.cell, classes.header, classes.column)}
          >
            {column.content}
          </Box>
        )
      )}

      {rows.map((row, index) =>
        popover(
          row.dropdown,
          <Box
            key={row.key}
            onClick={row.onClick}
            onMouseDown={handleRowMouseDown(row.key)}
            style={cellStyle(-1, index)}
            className={cn(classes.cell, classes.header, classes.row)}
          >
            {row.content}
          </Box>
        )
      )}

      {rows.map((row, r) =>
        columns.map((column, c) => {
          const key = `${row.key}${cellKeyDelimiter}${column.key}`;
          const cell = cellMap.get(key) ?? defaultCell?.(key);
          const selected = selectionSet.has(key);
          const selectedAt = (dr: number, dc: number) =>
            selectionSet.has(
              `${rows[r + dr]?.key}${cellKeyDelimiter}${columns[c + dc]?.key}`
            );
          return popover(
            cell?.dropdown,
            <Box
              key={key}
              onClick={cell?.onClick}
              onMouseDown={handleCellMouseDown(key)}
              onMouseEnter={handleCellMouseEnter(key)}
              style={cellStyle(c, r)}
              className={cn(
                classes.cell,
                selected && [
                  classes.selected,
                  selection.length === 1 && classes.singleSelected,
                  selectedAt(-1, 0) && classes.hasTop,
                  selectedAt(1, 0) && classes.hasBottom,
                  selectedAt(0, -1) && classes.hasLeft,
                  selectedAt(0, 1) && classes.hasRight
                ]
              )}
            >
              {cell?.content}
            </Box>
          );
        })
      )}

      {extraColumn && (
        <>
          {popover(
            extraColumn.dropdown,
            <Box
              onClick={extraColumn.onClick}
              style={cellStyle(columns.length, -1)}
              className={cn(classes.cell, classes.header, classes.column)}
            >
              {extraColumn.content}
            </Box>
          )}
          {times(rows.length, index => (
            <Box
              key={index}
              style={cellStyle(columns.length, index)}
              className={classes.cell}
            />
          ))}
        </>
      )}

      {extraRow && (
        <>
          {popover(
            extraRow.dropdown,
            <Box
              onClick={extraRow.onClick}
              style={cellStyle(-1, rows.length)}
              className={cn(classes.cell, classes.header, classes.row)}
            >
              {extraRow.content}
            </Box>
          )}
          {times(columns.length, index => (
            <Box
              key={index}
              style={cellStyle(index, rows.length)}
              className={classes.cell}
            />
          ))}
        </>
      )}

      {extraColumn && extraRow && (
        <Box
          style={cellStyle(columns.length, rows.length)}
          className={classes.cell}
        />
      )}
    </Box>
  );
};
