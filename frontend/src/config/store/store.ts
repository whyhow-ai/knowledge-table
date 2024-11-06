import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  castArray,
  cloneDeep,
  compact,
  fromPairs,
  groupBy,
  isArray,
  isEmpty,
  isNil,
  keyBy,
  mapValues,
  omit
} from "lodash-es";
import cuid from "@bugsnag/cuid";
import {
  getBlankColumn,
  getBlankRow,
  getBlankTable,
  getCellKey,
  getInitialData,
  isArrayType,
  toSingleType
} from "./store.utils";
import { AnswerTableRow, SourceData, Store } from "./store.types";
import { runQuery, uploadFile } from "../api";
import { insertAfter, insertBefore, where } from "@utils/functions";

export const useStore = create<Store>()(
  persist(
    (set, get) => ({
      colorScheme: "light",
      ...getInitialData(),

      toggleColorScheme: () => {
        set({ colorScheme: get().colorScheme === "light" ? "dark" : "light" });
      },

      getTable: (id = get().activeTableId) => {
        const current = get().tables.find(t => t.id === id);
        if (!current) {
          throw new Error(`No table with id ${id}`);
        }
        return current;
      },

      addTable: name => {
        const newTable = getBlankTable(name);
        set({
          tables: [...get().tables, newTable],
          activeTableId: newTable.id
        });
      },

      editTable: (id, table) => {
        set({ tables: where(get().tables, t => t.id === id, table) });
      },

      editActiveTable: table => {
        get().editTable(get().activeTableId, table);
      },

      switchTable: id => {
        if (get().tables.find(t => t.id === id)) {
          set({ activeTableId: id });
        }
      },

      deleteTable: id => {
        const { tables, activeTableId } = get();
        const nextTables = tables.filter(t => t.id !== id);
        if (isEmpty(nextTables)) return;
        const nextActiveTable =
          activeTableId === id ? nextTables[0].id : activeTableId;
        set({ tables: nextTables, activeTableId: nextActiveTable });
      },

      insertColumnBefore: id => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          columns: insertBefore(
            getTable().columns,
            getBlankColumn(),
            id ? c => c.id === id : undefined
          )
        });
      },

      insertColumnAfter: id => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          columns: insertAfter(
            getTable().columns,
            getBlankColumn(),
            id ? c => c.id === id : undefined
          )
        });
      },

      editColumn: (id, column) => {
        // TODO (maybe): Handle column type changes
        const { getTable, editActiveTable } = get();
        editActiveTable({
          columns: where(getTable().columns, column => column.id === id, column)
        });
      },

      rerunColumns: ids => {
        const { getTable, rerunCells } = get();
        rerunCells(
          getTable()
            .rows.filter(row => !row.hidden)
            .flatMap(row => ids.map(id => ({ rowId: row.id, columnId: id })))
        );
      },

      clearColumns: ids => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          rows: getTable().rows.map(row => ({
            ...row,
            cells: omit(row.cells, ids)
          }))
        });
      },

      unwindColumn: id => {
        const { getTable, editActiveTable } = get();
        const { rows, columns } = getTable();
        const newRows: AnswerTableRow[] = [];
        const column = columns.find(c => c.id === id);
        if (!column || !isArrayType(column.type)) return;

        for (const row of rows) {
          const pivot = row.cells[id];
          if (!isArray(pivot)) continue;
          for (const part of pivot) {
            const newRow: AnswerTableRow = {
              id: cuid(),
              sourceData: row.sourceData,
              hidden: false,
              cells: {}
            };
            newRows.push(newRow);
            for (const column of columns) {
              newRow.cells[column.id] =
                column.id === id ? part : row.cells[column.id];
            }
          }
        }

        editActiveTable({
          rows: newRows,
          columns: where(columns, column => column.id === id, {
            type: toSingleType(column.type)
          })
        });
      },

      toggleAllColumns: hidden => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          columns: getTable().columns.map(column => ({ ...column, hidden }))
        });
      },

      deleteColumns: ids => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          columns: getTable().columns.filter(
            column => !ids.includes(column.id)
          ),
          rows: getTable().rows.map(row => ({
            ...row,
            cells: omit(row.cells, ids)
          }))
        });
      },

      insertRowBefore: id => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          rows: insertBefore(
            getTable().rows,
            getBlankRow(),
            id ? c => c.id === id : undefined
          )
        });
      },

      insertRowAfter: id => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          rows: insertAfter(
            getTable().rows,
            getBlankRow(),
            id ? c => c.id === id : undefined
          )
        });
      },

      fillRow: async (id, file) => {
        const { activeTableId, getTable, editTable } = get();
        const sourceData: SourceData = {
          type: "document",
          document: await uploadFile(file)
        };
        editTable(activeTableId, {
          rows: where(getTable(activeTableId).rows, r => r.id === id, {
            sourceData,
            cells: {}
          })
        });
        get().rerunRows([id]);
      },

      fillRows: async files => {
        const { activeTableId, getTable, editTable } = get();
        editTable(activeTableId, { uploadingFiles: true });
        try {
          for (const file of files) {
            const sourceData: SourceData = {
              type: "document",
              document: await uploadFile(file)
            };
            const rows = getTable(activeTableId).rows;
            let id = rows.find(r => !r.sourceData)?.id;
            if (id) {
              editTable(activeTableId, {
                rows: where(rows, r => r.id === id, {
                  sourceData,
                  cells: {}
                })
              });
            } else {
              const newRow: AnswerTableRow = {
                id: (id = cuid()),
                sourceData,
                hidden: false,
                cells: {}
              };
              editTable(activeTableId, { rows: [...rows, newRow] });
            }
            get().rerunRows([id]);
          }
        } finally {
          editTable(activeTableId, { uploadingFiles: false });
        }
      },

      rerunRows: ids => {
        const { getTable, rerunCells } = get();
        rerunCells(
          getTable()
            .columns.filter(column => !column.hidden)
            .flatMap(column =>
              ids.map(id => ({ rowId: id, columnId: column.id }))
            )
        );
      },

      clearRows: ids => {
        const { getTable, editActiveTable } = get();
        const idSet = new Set(ids);
        editActiveTable({
          rows: where(getTable().rows, r => idSet.has(r.id), {
            sourceData: null,
            cells: {}
          })
        });
      },

      deleteRows: ids => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          rows: getTable().rows.filter(r => !ids.includes(r.id))
        });
      },

      editCells: (cells, tableId = get().activeTableId) => {
        const { getTable, editTable } = get();
        const valuesByRow = mapValues(
          groupBy(cells, c => c.rowId),
          c => c.map(c => [c.columnId, c.cell])
        );
        editTable(tableId, {
          rows: where(
            getTable(tableId).rows,
            r => valuesByRow[r.id],
            r => ({ cells: { ...r.cells, ...fromPairs(valuesByRow[r.id]) } })
          )
        });
      },

      rerunCells: cells => {
        const { activeTableId, getTable, editTable, editCells } = get();
        const { columns, rows, globalRules, loadingCells } = getTable();
        const colMap = keyBy(columns, c => c.id);
        const rowMap = keyBy(rows, r => r.id);

        const batch = compact(
          cells.map(({ rowId, columnId }) => {
            const key = getCellKey(rowId, columnId);
            const column = colMap[columnId];
            const row = rowMap[rowId];
            return column &&
              row &&
              column.entityType.trim() &&
              column.generate &&
              !loadingCells[key]
              ? { key, column, row }
              : null;
          })
        );

        editTable(activeTableId, {
          loadingCells: {
            ...loadingCells,
            ...fromPairs(batch.map(m => [m.key, true]))
          }
        });

        for (const { key, row, column: column_ } of batch) {
          const column = cloneDeep(column_);
          let shouldRunQuery = true;
          let hasMatches = false;

          // Replace all column references with the row's answer to that column
          for (const [match, columnId] of column.query.matchAll(
            /@\[[^\]]+\]\(([^)]+)\)/g
          )) {
            hasMatches = true;
            const targetColumn = columns.find(c => c.id === columnId);
            if (!targetColumn) continue;
            const cell = row.cells[targetColumn.id];
            if (isNil(cell) || (isNil(cell) && isNil(row.sourceData))) {
              shouldRunQuery = false;
              break;
            }
            column.query = column.query.replace(match, String(cell));
          }
          if (!hasMatches && isNil(row.sourceData)) {
            shouldRunQuery = false;
          }
          if (shouldRunQuery) {
            runQuery(row, column, globalRules).then(({ answer, chunks }) => {
              editCells(
                [{ rowId: row.id, columnId: column.id, cell: answer.answer }],
                activeTableId
              );
              editTable(activeTableId, {
                chunks: { ...getTable(activeTableId).chunks, [key]: chunks },
                loadingCells: omit(getTable(activeTableId).loadingCells, key)
              });
            });
          } else {
            editTable(activeTableId, {
              loadingCells: omit(getTable(activeTableId).loadingCells, key)
            });
          }
        }
      },

      clearCells: cells => {
        const { getTable, editActiveTable } = get();
        const columnsByRow = mapValues(
          groupBy(cells, c => c.rowId),
          c => c.map(c => c.columnId)
        );
        editActiveTable({
          rows: where(
            getTable().rows,
            r => columnsByRow[r.id],
            r => ({ cells: omit(r.cells, columnsByRow[r.id]) })
          )
        });
      },

      addGlobalRules: rules => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          globalRules: [
            ...getTable().globalRules,
            ...rules.map(rule => ({ id: cuid(), ...rule }))
          ]
        });
      },

      editGlobalRule: (id, rule) => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          globalRules: where(
            getTable().globalRules,
            rule => rule.id === id,
            rule
          )
        });
      },

      deleteGlobalRules: ids => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          globalRules: !ids
            ? []
            : getTable().globalRules.filter(rule => !ids.includes(rule.id))
        });
      },

      openChunks: cells => {
        get().editActiveTable({
          openedChunks: cells.map(c => getCellKey(c.rowId, c.columnId))
        });
      },

      closeChunks: () => {
        get().editActiveTable({ openedChunks: [] });
      },

      addFilter: filter => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          filters: [...getTable().filters, { id: cuid(), ...filter }]
        });
        get().applyFilters();
      },

      editFilter: (id, filter) => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          filters: where(getTable().filters, filter => filter.id === id, filter)
        });
        get().applyFilters();
      },

      deleteFilters: ids => {
        const { getTable, editActiveTable } = get();
        editActiveTable({
          filters: !ids
            ? []
            : getTable().filters.filter(filter => !ids.includes(filter.id))
        });
        get().applyFilters();
      },

      applyFilters: () => {
        const { getTable, editActiveTable } = get();
        const { rows, columns, filters } = getTable();
        editActiveTable({
          rows: rows.map(row => {
            const visible = filters.every(filter => {
              if (!filter.value.trim()) return true;
              const column = columns.find(
                column => column.id === filter.columnId
              );
              if (!column) return true;
              const cell = row.cells[column.id];
              if (isNil(cell)) return true;
              const contains = castArray(cell)
                .map(value => String(value).toLowerCase())
                .some(value =>
                  value.includes(filter.value.trim().toLowerCase())
                );
              return filter.criteria === "contains" ? contains : !contains;
            });
            return { ...row, hidden: !visible };
          })
        });
      },

      clear: allTables => {
        if (allTables) {
          set(getInitialData());
        } else {
          const { id, name, ...table } = getBlankTable();
          get().editActiveTable(table);
        }
      }
    }),
    {
      name: "store",
      version: 9
    }
  )
);
