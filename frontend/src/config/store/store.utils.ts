import cuid from "@bugsnag/cuid";
import { isArray, isEmpty, isNil, isString, times } from "lodash-es";
import {
  AnswerTable,
  AnswerTableColumn,
  AnswerTableRow,
  AnswerTableRule,
  CellKey,
  CellValue,
  Store
} from "./store.types";

export const DEFAULT_COLUMN_WIDTH = 160;

export function isArrayType(type: AnswerTableColumn["type"]) {
  return type === "int_array" || type === "str_array";
}

export function toSingleType(type: AnswerTableColumn["type"]) {
  return type === "int_array" ? "int" : type === "str_array" ? "str" : type;
}

export function getCellKey(
  row: AnswerTableRow | string,
  column: AnswerTableColumn | string
): CellKey {
  const rowId = isString(row) ? row : row.id;
  const columnId = isString(column) ? column : column.id;
  return `${rowId}-${columnId}`;
}

export function getBlankColumn(): AnswerTableColumn {
  return {
    id: cuid(),
    width: DEFAULT_COLUMN_WIDTH,
    hidden: false,
    entityType: "",
    type: "str",
    generate: true,
    query: "",
    rules: []
  };
}

export function getBlankRow(): AnswerTableRow {
  return {
    id: cuid(),
    sourceData: null,
    hidden: false,
    cells: {}
  };
}

export function getBlankTable(name?: string): AnswerTable {
  return {
    id: cuid(),
    name: name ?? "First Table",
    columns: times(10, getBlankColumn),
    rows: times(100, getBlankRow),
    globalRules: [],
    filters: [],
    chunks: {},
    openedChunks: [],
    loadingCells: {},
    uploadingFiles: false
  };
}

export function getInitialData(): Pick<Store, "tables" | "activeTableId"> {
  const initialTable = getBlankTable();
  return {
    tables: [initialTable],
    activeTableId: initialTable.id
  };
}

// Rules

export const defaultRules: Record<AnswerTableRule["type"], AnswerTableRule> = {
  must_return: { type: "must_return", options: [] },
  may_return: { type: "may_return", options: [] },
  max_length: { type: "max_length", length: 1 },
  resolve_entity: { type: "resolve_entity", options: [] }
};

export const ruleOptions: {
  value: AnswerTableRule["type"];
  label: string;
}[] = [
  { value: "must_return", label: "Must return" },
  { value: "may_return", label: "May return" },
  { value: "max_length", label: "Allowed # of responses" },
  { value: "resolve_entity", label: "Resolve entity" }
];

export const ruleInfo: Record<AnswerTableRule["type"], string> = {
  must_return: "The column must return the specified values",
  may_return: "The column may return the specified values",
  max_length: "The column must return at most N values",
  resolve_entity:
    "Replace all specified values with the first one from the list (i.e. 'turquioise:blue')"
};

// Casting

// const DELIMITER = "\x1f"; // If an uncommon delimiter is needed
const DELIMITER = ",";

export function castToInt(value: CellValue) {
  const str = castToString(value);
  if (isNil(str)) return str;
  const int = parseInt(str);
  return isNaN(int) ? undefined : int;
}

export function castToString(value: CellValue) {
  if (isNil(value)) return value;
  if (isArray(value)) {
    value = value.join(DELIMITER);
  }
  return String(value).trim() || undefined;
}

export function castToBool(value: CellValue) {
  let str = castToString(value);
  if (isNil(str)) return str;
  str = str.toLowerCase();
  return str === "true" ? true : str === "false" ? false : undefined;
}

export function castToIntArray(value: CellValue) {
  const str = castToString(value);
  if (isNil(str)) return str;
  const intArrayValue = str
    .split(DELIMITER)
    .map(castToInt)
    .filter(v => !isNil(v));
  return isEmpty(intArrayValue) ? undefined : intArrayValue;
}

export function castToStrArray(value: CellValue) {
  const str = castToString(value);
  if (isNil(str)) return str;
  const strArrayValue = str
    .split(DELIMITER)
    .map(castToString)
    .filter((v): v is string => !!v);
  return isEmpty(strArrayValue) ? undefined : strArrayValue;
}

export function castToType(
  value: CellValue,
  type: AnswerTableColumn["type"]
): CellValue {
  switch (type) {
    case "int":
      return castToInt(value);
    case "str":
      return castToString(value);
    case "bool":
      return castToBool(value);
    case "int_array":
      return castToIntArray(value);
    case "str_array":
      return castToStrArray(value);
  }
}
