import { createWithEqualityFn } from "zustand/traditional";
import { persist } from "zustand/middleware";
import {
  castArray,
  clamp,
  cloneDeep,
  compact,
  differenceBy,
  differenceWith,
  isArray,
  isMatch,
  partition,
  uniq
} from "lodash-es";
import cuid from "@bugsnag/cuid";
import {
  AnswerTableCell,
  AnswerTableColumn,
  AnswerTableRow,
  Store
} from "./store.types";
import { deleteDocument, runQuery, uploadFile } from "../api";
import { toSingleType } from "./store.utils";
import { where } from "@utils/functions";

export const useStore = createWithEqualityFn(
  persist<Store>(
    (set, get) => ({
      colorScheme: "light",
      columns: [],
      rows: [],
      cells: [],
      filters: [],
      selection: [],
      uploadingFiles: false,

      toggleColorScheme: () => {
        set({ colorScheme: get().colorScheme === "light" ? "dark" : "light" });
      },

      addColumn: prompt => {
        const id = cuid();
        const column: AnswerTableColumn = {
          id,
          prompt: { id, ...prompt },
          width: 240,
          hidden: false
        };
        set({ columns: [...get().columns, column] });
        get()._syncAnswers();
      },

      clearAllData: () => {
        set({
          columns: [],
          rows: [],
          cells: [],
          filters: [],
          selection: [],
          uploadingFiles: false
        });
      },

      editColumn: (id, prompt) => {
        set({
          columns: where(
            get().columns,
            column => column.id === id,
            column => ({ ...column, prompt: { ...column.prompt, ...prompt } })
          )
        });
      },

      resizeColumn: (id, width) => {
        set({
          columns: where(get().columns, column => column.id === id, {
            width: clamp(width, 160, 2000)
          })
        });
      },

      rerunColumn: id => {
        set({ cells: get().cells.filter(cell => cell.columnId !== id) });
        get()._syncAnswers();
      },

      unwindColumn: id => {
        const { rows, columns } = get();
        const cellMap = get()._getCellMap();
        const newRows: AnswerTableRow[] = [];
        const newCells: AnswerTableCell[] = [];

        for (const row of rows) {
          const pivot = cellMap.get(`${row.id}-${id}`);
          if (!pivot || !isArray(pivot.answer.answer)) continue;
          for (const answer of pivot.answer.answer) {
            const newRow: AnswerTableRow = {
              id: cuid(),
              document: row.document,
              hidden: false
            };
            newRows.push(newRow);
            for (const column of columns) {
              const cell = cellMap.get(`${row.id}-${column.id}`);
              if (!cell) continue;
              newCells.push({
                columnId: column.id,
                rowId: newRow.id,
                dirty: false,
                answer:
                  cell !== pivot
                    ? cell.answer
                    : {
                        ...cell.answer,
                        id: cuid(),
                        type: toSingleType(cell.answer.type),
                        answer
                      }
              });
            }
          }
        }

        set({
          rows: newRows,
          cells: newCells,
          columns: where(
            columns,
            column => column.id === id,
            column => ({
              ...column,
              prompt: {
                ...column.prompt,
                type: toSingleType(column.prompt.type)
              }
            })
          )
        });
      },

      toggleColumn: (id, hidden) => {
        set({
          selection: [],
          columns: where(get().columns, column => column.id === id, { hidden })
        });
      },

      toggleAllColumns: hidden => {
        set({
          selection: [],
          columns: get().columns.map(column => ({ ...column, hidden }))
        });
      },

      deleteColumns: ids => {
        set({
          selection: [],
          columns: get().columns.filter(column => !ids.includes(column.id)),
          cells: get().cells.filter(cell => !ids.includes(cell.columnId))
        });
      },

      addRows: async files => {
        set({ uploadingFiles: true });
        try {
          for (const file of files) {
            const row: AnswerTableRow = {
              id: cuid(),
              document: await uploadFile(file),
              hidden: false
            };
            set({ rows: [...get().rows, row] });
            get()._syncAnswers();
          }
        } finally {
          set({ uploadingFiles: false });
        }
      },

      rerunRow: id => {
        set({ cells: get().cells.filter(cell => cell.rowId !== id) });
        get()._syncAnswers();
      },

      deleteRows: async ids => {
        const [rowsToDelete, rowsToKeep] = partition(get().rows, row =>
          ids.includes(row.id)
        );
        const documentsToDelete = uniq(
          differenceBy(rowsToDelete, rowsToKeep, row => row.document.id).map(
            row => row.document.id
          )
        );
        set({
          selection: [],
          rows: rowsToKeep,
          cells: get().cells.filter(cell => !ids.includes(cell.rowId))
        });
        await Promise.all(documentsToDelete.map(deleteDocument));
      },

      editCell: (cell, answer) => {
        set({
          cells: where(
            get().cells,
            c => c.rowId === cell.rowId && c.columnId === cell.columnId,
            c => ({ ...c, answer: { ...c.answer, ...answer } })
          )
        });
      },

      rerunCells: cells => {
        set({ cells: differenceWith(get().cells, cells, isMatch) });
        get()._syncAnswers();
      },

      addFilter: filter => {
        set({ filters: [...get().filters, { id: cuid(), ...filter }] });
        get().applyFilters();
      },

      editFilter: (id, filter) => {
        set({
          filters: where(get().filters, filter => filter.id === id, filter)
        });
        get().applyFilters();
      },

      deleteFilters: ids => {
        set({
          filters: !ids
            ? []
            : get().filters.filter(filter => !ids.includes(filter.id))
        });
        get().applyFilters();
      },

      applyFilters: () => {
        const { rows, columns, filters } = get();
        const cellMap = get()._getCellMap();
        set({
          rows: rows.map(row => {
            const visible = filters.every(filter => {
              if (!filter.value.trim()) return true;
              const column = columns.find(
                column => column.id === filter.columnId
              );
              if (!column) return true;
              const cell = cellMap.get(`${row.id}-${column.id}`);
              if (!cell) return true;
              const answer = cell.answer.answer;
              if (answer === null) return true;
              const contains = castArray(answer)
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

      _syncAnswers: async () => {
        const { rows, columns } = get();
        const cellMap = get()._getCellMap();

        const missingAnswers = compact(
          rows.flatMap(row =>
            columns.map(column => {
              const cell = cellMap.get(`${row.id}-${column.id}`);
              if (cell && !cell.dirty) return null;
              return { row, column, cell };
            })
          )
        );

        for (const missing of missingAnswers) {
          const prompt = cloneDeep(missing.column.prompt);

          // Replace all {entityType} with the row's answer to that entity's prompt
          for (const [match, key] of prompt.query.matchAll(/\{([^{}]+)\}/g)) {
            const column = get().columns.find(
              ({ prompt }) => prompt.entityType === key
            );
            if (!column) continue;
            const cell = cellMap.get(`${missing.row.id}-${column.id}`);
            if (!cell) continue;
            prompt.query = prompt.query.replace(
              match,
              String(cell.answer.answer)
            );
          }

          runQuery(missing.row.document.id, prompt).then(answer =>
            get()._upsertCell({
              columnId: missing.column.id,
              rowId: missing.row.id,
              dirty: false,
              answer
            })
          );
        }
      },

      _upsertCell: cell => {
        const cells = [...get().cells];
        const index = cells.findIndex(
          c => c.rowId === cell.rowId && c.columnId === cell.columnId
        );
        if (index === -1) {
          set({ cells: [...cells, cell] });
        } else {
          cells[index] = cell;
          set({ cells });
        }
      },

      _getCellMap: () => {
        const { cells } = get();
        return new Map(
          cells.map(cell => [`${cell.rowId}-${cell.columnId}`, cell])
        );
      }
    }),
    {
      name: "store",
      version: 4
    }
  )
);
