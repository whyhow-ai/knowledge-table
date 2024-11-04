import { z } from "zod";
import {
  isArray,
  isNil,
  isPlainObject,
  isString,
  mapValues,
  omit
} from "lodash-es";
import {
  AnswerTableColumn,
  AnswerTableGlobalRule,
  AnswerTableRow
} from "./store";

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

export const chunkSchema = z
  .object({
    content: z.string(),
    page: z.number()
  })
  .strict();

export const answerSchema = z.union([
  z.null(),
  z.number(),
  z.string(),
  z.boolean(),
  z.array(z.number()),
  z.array(z.string())
]);

export const resolvedEntitySchema = z.object({
  original: z.union([z.string(), z.array(z.string())]),
  resolved: z.union([z.string(), z.array(z.string())]),
  source: z.object({
    type: z.string(),
    id: z.string()
  }),
  entityType: z.string()
});

// Update the resolved entities schema to match backend format
export const resolvedEntitiesSchema = z.union([
  z.array(resolvedEntitySchema),
  z.null(),
  z.undefined()
]);

// Update the query response schema
const queryResponseSchema = z.object({
  answer: z.object({ answer: answerSchema }),
  chunks: z.array(chunkSchema),
  resolved_entities: resolvedEntitiesSchema
});

// Update the runQuery function to transform the data format
export async function runQuery(
  row: AnswerTableRow,
  column: AnswerTableColumn,
  globalRules: AnswerTableGlobalRule[]
) {
  if (!column.entityType.trim() || !column.generate) {
    throw new Error(
      "Row or column doesn't allow running query (missing row source data or column is empty or has generate set to false)"
    );
  }
  const rules = [
    ...column.rules,
    ...globalRules
      .filter(rule => rule.entityType.trim() === column.entityType.trim())
      .map(r => omit(r, "id", "entityType"))
  ];
  
  const result = await fetch("http://localhost:8000/api/v1/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      document_id: row.sourceData?.document?.id
        ? row.sourceData.document.id
        : "00000000000000000000000000000000",
      prompt: {
        id: column.id,
        entity_type: column.entityType,
        query: column.query,
        type: column.type,
        rules
      }
    })
  });
  
  const response = await result.json();
  console.log('Raw API Response:', response);
  
  const parsed = queryResponseSchema.parse(response);
  console.log('Parsed Response:', parsed);
  
  // Update resolved entities transformation to handle the new format
  const resolvedEntities = parsed.resolved_entities?.map(entity => ({
    original: entity.original,
    resolved: entity.resolved,
    source: entity.source,
    entityType: entity.entityType,
    fullAnswer: parsed.answer.answer as string
  })) ?? null;
  
  console.log('Transformed Resolved Entities:', resolvedEntities);

  return {
    answer: parsed.answer,
    chunks: parsed.chunks,
    resolvedEntities
  };
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
