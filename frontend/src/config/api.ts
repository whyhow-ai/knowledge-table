import { z } from "zod";
import { isArray, isNil, isPlainObject, isString, mapValues } from "lodash-es";
import { Prompt } from "./store";

// Upload file

export const documentSchema = z
  .object({
    id: z.string(),
    name: z.string(),
    author: z.string(),
    tag: z.string(),
    page_count: z.number()
  })
  .strict();

export async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const result = await fetch("http://localhost:8000/api/v1/document", {
    method: "POST",
    body: formData
  });
  return documentSchema.parse(await result.json());
}

// Delete document

export async function deleteDocument(id: string) {
  await fetch(`http://localhost:8000/api/v1/document/${id}`, {
    method: "DELETE"
  });
}

// Run query

export const answerSchema = z
  .object({
    id: z.string(),
    document_id: z.string(),
    prompt_id: z.string(),
    type: z.enum(["int", "str", "bool", "int_array", "str_array"]),
    answer: z.union([
      z.null(),
      z.number(),
      z.string(),
      z.boolean(),
      z.array(z.number()),
      z.array(z.string())
    ]),
    chunks: z.array(
      z
        .object({
          content: z.string(),
          page: z.number()
        })
        .strict()
    )
  })
  .strict();

export async function runQuery(
  documentId: string,
  prompt: Prompt,
  previousAnswer?: number | string | boolean | number[] | string[]
) {
  const result = await fetch("http://localhost:8000/api/v1/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      document_id: documentId,
      previous_answer: previousAnswer,
      prompt: {
        id: prompt.id,
        entity_type: prompt.entityType,
        query: prompt.query,
        type: prompt.type,
        rules: prompt.rules
      }
    })
  });
  return answerSchema.parse(await result.json());
}

// Export triples

export async function exportTriples(tableData: any) {
  function stringifyDeep(value: any): any {
    if (isNil(value)) {
      return "";
    } else if (isString(value)) {
      return value;
    } else if (isArray(value)) {
      return value.map(stringifyDeep);
    } else if (isPlainObject(value)) {
      return mapValues(value, stringifyDeep);
    } else {
      return String(value);
    }
  }

  return fetch("http://localhost:8000/api/v1/graph/export-triples", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(stringifyDeep(tableData))
  }).then(r => r.blob());
}
