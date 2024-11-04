import { z } from "zod";
import { answerSchema, documentSchema, chunkSchema } from "../api";

export interface Store {
  colorScheme: "light" | "dark";
  tables: AnswerTable[];
  activeTableId: string;

  toggleColorScheme: () => void;

  getTable: (id?: string) => AnswerTable;
  addTable: (name: string) => void;
  editTable: (id: string, table: Partial<AnswerTable>) => void;
  editActiveTable: (table: Partial<AnswerTable>) => void;
  switchTable: (id: string) => void;
  deleteTable: (id: string) => void;

  insertColumnBefore: (id?: string) => void;
  insertColumnAfter: (id?: string) => void;
  editColumn: (id: string, column: Partial<AnswerTableColumn>) => void;
  rerunColumns: (ids: string[]) => void;
  clearColumns: (ids: string[]) => void;
  unwindColumn: (id: string) => void;
  toggleAllColumns: (hidden: boolean) => void;
  deleteColumns: (ids: string[]) => void;

  insertRowBefore: (id?: string) => void;
  insertRowAfter: (id?: string) => void;
  fillRow: (id: string, file: File) => Promise<void>;
  fillRows: (files: File[]) => Promise<void>;
  rerunRows: (ids: string[]) => void;
  clearRows: (ids: string[]) => void;
  deleteRows: (ids: string[]) => void;

  editCells: (
    cells: { rowId: string; columnId: string; cell: CellValue }[],
    tableId?: string
  ) => void;
  rerunCells: (cells: { rowId: string; columnId: string }[]) => void;
  clearCells: (cells: { rowId: string; columnId: string }[]) => void;

  addGlobalRules: (rules: Omit<AnswerTableGlobalRule, "id">[]) => void;
  editGlobalRule: (id: string, rule: Partial<AnswerTableGlobalRule>) => void;
  deleteGlobalRules: (ids?: string[]) => void;

  openChunks: (cells: { rowId: string; columnId: string }[]) => void;
  closeChunks: () => void;

  addFilter: (filter: Omit<AnswerTableFilter, "id">) => void;
  editFilter: (id: string, filter: Partial<AnswerTableFilter>) => void;
  deleteFilters: (ids?: string[]) => void;
  applyFilters: () => void;

  clear: (allTables?: boolean) => void;
}

export interface ResolvedEntity {
  original: string | string[];  // Allow both string and array of strings
  resolved: string | string[];  // Allow both string and array of strings
  fullAnswer: string;
  entityType: string;
  source: {
    type: 'global' | 'column';
    id: string;
  };
}

export interface AnswerTable {
  id: string;
  name: string;
  columns: AnswerTableColumn[];
  rows: AnswerTableRow[];
  globalRules: AnswerTableGlobalRule[];
  filters: AnswerTableFilter[];
  chunks: Record<CellKey, Chunk[]>;
  openedChunks: CellKey[];
  loadingCells: Record<CellKey, true>;
  uploadingFiles: boolean;
}

export interface AnswerTableColumn {
  id: string;
  width: number;
  hidden: boolean;
  entityType: string;
  type: "int" | "str" | "bool" | "int_array" | "str_array";
  generate: boolean;
  query: string;
  rules: AnswerTableRule[];
  resolvedEntities?: ResolvedEntity[];
}

export interface AnswerTableRow {
  id: string;
  sourceData: SourceData | null;
  hidden: boolean;
  cells: Record<string, CellValue>;
}

export interface AnswerTableFilter {
  id: string;
  columnId: string;
  criteria: "contains" | "contains_not";
  value: string;
}

export interface AnswerTableGlobalRule extends AnswerTableRule {
  id: string;
  entityType: string;
  resolvedEntities?: ResolvedEntity[];
}

export interface AnswerTableRule {
  type: "must_return" | "may_return" | "max_length" | "resolve_entity";
  options?: string[];
  length?: number;
}

export type SourceData = {
  type: "document";
  document: Document;
};

export type CellKey = `${string}-${string}`;
export type Document = z.infer<typeof documentSchema>;
export type CellValue = z.infer<typeof answerSchema> | undefined;
export type Chunk = z.infer<typeof chunkSchema>;
