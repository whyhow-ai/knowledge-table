# Tutorial: Extracting Data from Documents

This tutorial walks you through the process of extracting structured data from documents using Knowledge Table.

## Prerequisites

- Knowledge Table backend running.
- OpenAI API key configured.

## Steps

1. **Upload a Document**

   Use the `/documents/` endpoint to upload a document.

   ```bash
   curl -X POST "http://localhost:8000/api/v1/documents/" \
   -H "accept: application/json" \
   -H "Content-Type: multipart/form-data" \
   -F "file=@/path/to/your/document.pdf"
   ```

2. **Define an Extraction Query**

   Use the `/queries/` endpoint to create a query.

   ```json
   {
     "question": "What is the main topic of the document?"
   }
   ```

3. **Retrieve the Answer**

   Use the `/queries/{id}/results/` endpoint to get the extracted data.

## Conclusion

You've successfully extracted data from a document. Explore other functionalities to get the most out of Knowledge Table.
