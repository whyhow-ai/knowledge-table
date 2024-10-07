import { Prompt } from "./store.types";

export function isArrayType(type: Prompt["type"]) {
  return type === "int_array" || type === "str_array";
}

export function toSingleType(type: Prompt["type"]) {
  return type === "int_array" ? "int" : type === "str_array" ? "str" : type;
}
