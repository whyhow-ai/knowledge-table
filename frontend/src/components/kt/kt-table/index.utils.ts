import { ReactGridProps, HeaderCell, CellChange } from "@silevis/reactgrid";
import { isEmpty, mapValues, uniqBy } from "lodash-es";
import { KtColumnCell, KtRowCell, KtCell } from "./kt-cells";
import { useStore } from "@config/store";
import { pack, plur } from "@utils/functions";

export type Cell = HeaderCell | KtColumnCell | KtRowCell | KtCell;

export const HEADER_ROW_ID = "header-row";
export const SOURCE_COLUMN_ID = "source-column";

export const handleCellChange = (changes: CellChange[]) => {
  const filteredChanges = (changes as CellChange<Cell>[]).filter(
    change =>
      change.rowId !== HEADER_ROW_ID &&
      change.columnId !== SOURCE_COLUMN_ID &&
      change.previousCell.type === "kt-cell" &&
      change.newCell.type === "kt-cell"
  );
  useStore.getState().editCells(
    filteredChanges.map(change => ({
      rowId: String(change.rowId),
      columnId: String(change.columnId),
      cell: (change.newCell as KtCell).cell
    }))
  );
};

export const handleContextMenu: Required<ReactGridProps>["onContextMenu"] = (
  selectedRowIds_,
  selectedColIds_,
  _,
  options,
  selectedRanges
) => {
  const store = useStore.getState();
  const rowIds = selectedRowIds_
    .filter(rowId => rowId !== HEADER_ROW_ID)
    .map(String);
  const colIds = selectedColIds_
    .filter(colId => colId !== SOURCE_COLUMN_ID)
    .map(String);

  const cells = uniqBy(
    selectedRanges
      .flat()
      .filter(
        c => c.rowId !== HEADER_ROW_ID && c.columnId !== SOURCE_COLUMN_ID
      ),
    c => `${c.rowId}-${c.columnId}`
  ).map(cell => mapValues(cell, String));

  return pack([
    !isEmpty(cells) &&
      isEmpty(rowIds) &&
      isEmpty(colIds) && [
        {
          id: "rerun-cells",
          label: `Rerun ${plur("cell", cells)}`,
          handler: () => store.rerunCells(cells)
        },
        {
          id: "clear-cells",
          label: `Clear ${plur("cell", cells)}`,
          handler: () => store.clearCells(cells)
        },
        {
          id: "chunks",
          label: "View chunks",
          handler: () => store.openChunks(cells)
        }
      ],
    ...options.filter(option => option.id !== "cut"),
    rowIds.length === 1 && [
      {
        id: "insert-row-before",
        label: "Insert row before",
        handler: () => store.insertRowBefore(rowIds[0])
      },
      {
        id: "insert-row-after",
        label: "Insert row after",
        handler: () => store.insertRowAfter(rowIds[0])
      }
    ],
    colIds.length === 1 && [
      {
        id: "insert-column-before",
        label: "Insert column before",
        handler: () => store.insertColumnBefore(colIds[0])
      },
      {
        id: "insert-column-after",
        label: "Insert column after",
        handler: () => store.insertColumnAfter(colIds[0])
      }
    ],
    !isEmpty(rowIds) && [
      {
        id: "rerun-rows",
        label: `Rerun ${plur("row", rowIds)}`,
        handler: () => store.rerunRows(rowIds)
      },
      {
        id: "clear-rows",
        label: `Clear ${plur("row", rowIds)}`,
        handler: () => store.clearRows(rowIds)
      },
      {
        id: "delete-rows",
        label: `Delete ${plur("row", rowIds)}`,
        handler: () => store.deleteRows(rowIds)
      }
    ],
    !isEmpty(colIds) && [
      {
        id: "rerun-columns",
        label: `Rerun ${plur("column", colIds)}`,
        handler: () => store.rerunColumns(colIds)
      },
      {
        id: "clear-columns",
        label: `Clear ${plur("column", colIds)}`,
        handler: () => store.clearColumns(colIds)
      },
      {
        id: "delete-columns",
        label: `Delete ${plur("column", colIds)}`,
        handler: () => store.deleteColumns(colIds)
      }
    ]
  ]);
};
