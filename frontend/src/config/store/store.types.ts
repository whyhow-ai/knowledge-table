import { z } from "zod";
import { answerSchema, documentSchema } from "../api";

export interface Store {
  colorScheme: "light" | "dark";
  columns: AnswerTableColumn[];
  rows: AnswerTableRow[];
  cells: AnswerTableCell[];
  filters: AnswerTableFilter[];
  selection: string[];
  uploadingFiles: boolean;

  toggleColorScheme: () => void;

  addColumn: (prompt: Omit<Prompt, "id">) => void;
  editColumn: (id: string, prompt: Omit<Prompt, "id">) => void;
  resizeColumn: (id: string, width: number) => void;
  rerunColumn: (id: string) => void;
  unwindColumn: (id: string) => void;
  toggleColumn: (id: string, hidden: boolean) => void;
  toggleAllColumns: (hidden: boolean) => void;
  deleteColumns: (ids: string[]) => void;

  clearAllData: () => void;

  addRows: (files: File[]) => Promise<void>;
  rerunRow: (id: string) => void;
  deleteRows: (ids: string[]) => Promise<void>;

  editCell: (
    cell: Pick<AnswerTableCell, "rowId" | "columnId">,
    answer: Partial<Answer>
  ) => void;
  rerunCells: (cells: Pick<AnswerTableCell, "rowId" | "columnId">[]) => void;

  addFilter: (filter: Omit<AnswerTableFilter, "id">) => void;
  editFilter: (id: string, filter: Partial<AnswerTableFilter>) => void;
  deleteFilters: (ids?: string[]) => void;
  applyFilters: () => void;

  _syncAnswers: () => Promise<void>;
  _upsertCell: (cell: AnswerTableCell) => void;
  _getCellMap: () => Map<string, AnswerTableCell>;
}

export type Document = z.infer<typeof documentSchema>;

export interface Prompt {
  id: string;
  entityType: string;
  query: string;
  type: "int" | "str" | "bool" | "int_array" | "str_array";
  rules: PromptRule[];
}

export type Answer = z.infer<typeof answerSchema>;

export type PromptRule =
  | {
      type: "must_return" | "may_return";
      options: string[];
    }
  | {
      type: "max_length";
      length: number;
    };

export interface AnswerTableColumn {
  id: string;
  prompt: Prompt;
  width: number;
  hidden: boolean;
}

export interface AnswerTableRow {
  id: string;
  document: Document;
  hidden: boolean;
}

export interface AnswerTableCell {
  columnId: string;
  rowId: string;
  dirty: boolean;
  answer: Answer;
}

export interface AnswerTableFilter {
  id: string;
  columnId: string;
  criteria: "contains" | "contains_not";
  value: string;
}
