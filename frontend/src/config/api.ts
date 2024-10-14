import { z } from "zod";
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
  await fetch(`http://localhost:8000/api/v1/document/${id}`, { method: "DELETE" });
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
    console.log('runQuery called with:', { documentId, prompt, previousAnswer });
    
    const requestBody = {
      document_id: documentId,
      previous_answer: previousAnswer,
      prompt: {
        id: prompt.id,
        entity_type: prompt.entityType,
        query: prompt.query,
        type: prompt.type,
        rules: prompt.rules
      }
    };
    
    console.log('Request body:', JSON.stringify(requestBody, null, 2));
  
    try {
      const result = await fetch("http://localhost:8000/api/v1/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
      });
  
      console.log('Response status:', result.status);
      console.log('Response headers:', Object.fromEntries(result.headers.entries()));
  
      if (!result.ok) {
        const errorText = await result.text();
        console.error('Error response body:', errorText);
        throw new Error(`HTTP error! status: ${result.status}, body: ${errorText}`);
      }
  
      const responseData = await result.json();
      console.log('Response data:', responseData);
  
      return answerSchema.parse(responseData);
    } catch (error) {
      console.error('Error in runQuery:', error);
      if (error instanceof Error) {
        console.error('Error message:', error.message);
        console.error('Error stack:', error.stack);
      }
      throw error;
    }
  }

// Helper function to convert any value to a string
function convertToString(value: any): string {
  if (typeof value === 'string') return value;
  if (value === null || value === undefined) return '';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
}

// Helper function to recursively convert all values in an object to strings
function convertObjectToStrings(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(convertObjectToStrings);
  } else if (typeof obj === 'object' && obj !== null) {
    return Object.fromEntries(
      Object.entries(obj).map(([key, value]) => [key, convertObjectToStrings(value)])
    );
  } else {
    return convertToString(obj);
  }
}

// Export triples
export async function exportTriples(tableData: any) {
  
  console.log('Exporting triples with data:', tableData);
  
  // Convert all data to strings
  const stringifiedData = convertObjectToStrings(tableData);
  
  console.log('Stringified data:', stringifiedData);
  
  try {
    const response = await fetch("http://localhost:8000/api/v1/graph/export-triples", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(stringifiedData) // Send the stringified data directly
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response body:', errorText);
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
    }

    const blob = await response.blob();
    console.log('Received blob:', blob);

    // Handle the blob (e.g., download it or process it further)
    // For example, you could create a link to download the blob:
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'triples.json'; 
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url); 

  } catch (error) {
    console.error('Error exporting triples:', error);
    if (error instanceof Error) {
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
    }
    throw error;
  }
}
