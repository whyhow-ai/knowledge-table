import { Button } from "@mantine/core";
import { IconDownload, IconShare } from "@tabler/icons-react";
import { exportTriples as apiExportTriples } from "../../../config/api";

interface Document {
  id: string;
  name: string;
}

interface Answer {
  answer: string | number | boolean | (string | number | boolean)[];
}

interface Cell {
  columnId: string;
  rowId: string;
  answer: Answer;
}

interface Column {
  id: string;
  prompt: {
    entityType: string;
  };
}

interface Row {
  id: string;
  document: Document;
}

interface Store {
  state: {
    columns: Column[];
    rows: Row[];
    cells: Cell[];
  };
}

// Ensure types are valid
const isArrayOfPrimitives = (
  answer: any
): answer is (string | number | boolean)[] => {
  return (
    Array.isArray(answer) &&
    answer.every((item) =>
      ["string", "number", "boolean"].includes(typeof item)
    )
  );
};

const downloadCSV = () => {
  const localStorageData = localStorage.getItem("store");

  // Check if data exists in localStorage and parse
  if (!localStorageData) {
    console.error("No data found.");
    return;
  }

  let data: Store;
  try {
    data = JSON.parse(localStorageData);
  } catch (error) {
    console.error("Could not parse localStorage:", error);
    return;
  }

  // Check that columns, rows, and cells are defined
  if (!data?.state?.columns || !data?.state?.rows || !data?.state?.cells) {
    console.error("No data to download.");
    return;
  }

  const columns = data.state.columns.map(
    (col) => col.prompt.entityType || "Unknown"
  );

  // Assume first column is the document name
  let csvData = `Document,${columns.join(",")}\n`;

  data.state.rows.forEach((row) => {
    const rowId = row?.id;
    const documentName = row?.document?.name || "Unknown";

    const cellValues = data.state.columns.map((col) => {
      const cell = data.state.cells.find(
        (cell) => cell.columnId === col.id && cell.rowId === rowId
      );

      if (cell && cell.answer) {
        const answer = cell.answer.answer;

        if (isArrayOfPrimitives(answer)) {
          // For simplicity, turn everything into a string, and join with a comma
          return `"${answer.join(", ")}"`;
        } else if (
          typeof answer === "string" ||
          typeof answer === "number" ||
          typeof answer === "boolean"
        ) {
          // Some single text answers include commas, wrap in quotes
          return `"${answer.toString()}"`;
        }
        return answer !== undefined ? `"${String(answer)}"` : "";
      }

      return "";
    });

    // Join all as a single row
    csvData += `"${documentName}",${cellValues.join(",")}\n`;
  });

  // Create blob and download
  const blob = new Blob([csvData], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "knowledge-table-data.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};

export const DownloadCsvButton = () => {
  return (
    <Button leftSection={<IconDownload />} onClick={downloadCSV}>
      Download CSV
    </Button>
  );
};

// export const ExportTriplesButton = () => {
//     const handleExportTriples = async () => {
//       const localStorageData = localStorage.getItem("store");
//       if (!localStorageData) {
//         console.error("No data found in localStorage.");
//         return;
//       }
  
//       const parsedData = JSON.parse(localStorageData);
//       console.log("Parsed data:", parsedData);
  
//       const { columns, rows, cells } = parsedData.state;
  
//       const triples = [];
//       const chunks = [];
//       let tripleIdCounter = 1;
  
//       rows.forEach((row) => {
//         const documentName = row.document?.name || "Unknown Document";
  
//         columns.forEach((column, columnIndex) => {
//           const cell = cells.find(cell => cell.columnId === column.id && cell.rowId === row.id);
//           if (!cell || !cell.answer) return;
  
//           const entityType = column.prompt?.entityType || "Unknown";
//           const cellContent = Array.isArray(cell.answer.answer) 
//             ? cell.answer.answer.join(", ") 
//             : cell.answer.answer.toString();
  
//           // Find the page number from the first chunk
//           let page = '1'; // Default value
//           if (cell.answer.chunks && cell.answer.chunks.length > 0) {
//             page = cell.answer.chunks[0].page.toString();
//             console.log('Page found in cell.answer.chunks:', page);
//           } else {
//             console.log('No page number found in chunks, using default:', page);
//           }

//           console.log("Document name:", documentName);

//           // Create entity-document triple
//           const entityDocumentTriple = {
//             triple_id: `t${tripleIdCounter++}`,
//             head: { label: "Document", name: documentName },
//             tail: { label: entityType, name: cellContent },
//             relation: { name: "contains" },
//             chunk_ids: []
//           };
//           triples.push(entityDocumentTriple);

//           // Create chunks for the cell's answer
//           if (cell.answer.chunks && cell.answer.chunks.length > 0) {
//             cell.answer.chunks.forEach((chunk, index) => {
//               const chunkId = `${entityDocumentTriple.triple_id}_${row.id}_c${index + 1}`;
//               chunks.push({
//                 chunk_id: chunkId,
//                 content: chunk.content,
//                 page: chunk.page.toString(),
//                 triple_id: entityDocumentTriple.triple_id
//               });
//               entityDocumentTriple.chunk_ids.push(chunkId);
//             });
//           } else {
//             // Fallback if no chunks are available
//             const chunkId = `${entityDocumentTriple.triple_id}_${row.id}_c1`;
//             chunks.push({
//               chunk_id: chunkId,
//               content: cellContent,
//               page: "1",
//               triple_id: entityDocumentTriple.triple_id
//             });
//             entityDocumentTriple.chunk_ids.push(chunkId);
//           }
  
//           // Create entity-entity triples for all other columns
//           columns.forEach((otherColumn, otherIndex) => {
//             if (otherIndex <= columnIndex) return; // Avoid duplicate triples
  
//             const otherCell = cells.find(cell => cell.columnId === otherColumn.id && cell.rowId === row.id);
//             if (!otherCell || !otherCell.answer) return;
  
//             const otherEntityType = otherColumn.prompt?.entityType || "Unknown";
//             const otherCellContent = Array.isArray(otherCell.answer.answer)
//               ? otherCell.answer.answer.join(", ")
//               : otherCell.answer.answer.toString();
  
//             const entityEntityTriple = {
//               triple_id: `t${tripleIdCounter++}`,
//               head: { label: entityType, name: cellContent },
//               tail: { label: otherEntityType, name: otherCellContent },
//               relation: { name: "related_to" },
//               chunk_ids: []
//             };
//             triples.push(entityEntityTriple);
  
//             // Create chunks for both entities
//             [cellContent, otherCellContent].forEach((content, index) => {
//                 const chunkId = `${entityEntityTriple.triple_id}_${row.id}_c${index + 1}`;
            
//                 // Attempt to find page number
//                 let page = '1'; // Default value
//                 if (cell.page) {
//                 page = cell.page;
//                 console.log('Page found in cell:', page);
//                 } else if (row.page) {
//                 page = row.page;
//                 console.log('Page found in row:', page);
//                 } else {
//                 console.log('No page number found, using default:', page);
//                 }
            
//                 chunks.push({
//                 chunk_id: chunkId,
//                 content: content,
//                 page: "1",
//                 triple_id: entityEntityTriple.triple_id
//                 });
//                 console.log('Created chunk:', chunks[chunks.length - 1]);
            
//                 entityEntityTriple.chunk_ids.push(chunkId);
//             });
//           });
//         });
//       });
  
//       const output = { triples, chunks };
//       console.log("Final output:", output);
  
//       // Download the JSON file
//       const blob = new Blob([JSON.stringify(output, null, 2)], { type: 'application/json' });
//       const url = URL.createObjectURL(blob);
//       const a = document.createElement('a');
//       a.href = url;
//       a.download = 'exported_triples.json';
//       document.body.appendChild(a);
//       a.click();
//       document.body.removeChild(a);
//       URL.revokeObjectURL(url);
//     };
  
//     return (
//       <Button leftSection={<IconShare />} onClick={handleExportTriples}>
//         Export to Triples
//       </Button>
//     );
//   };

export const ExportTriplesButton = () => {
    const handleExportTriples = async () => {
      const localStorageData = localStorage.getItem("store");
      if (!localStorageData) {
        console.error("No data found.");
        return;
      }
  
      let data: Store;
      try {
        data = JSON.parse(localStorageData);
      } catch (error) {
        console.error("Could not parse localStorage:", error);
        return;
      }
  
      if (!data?.state?.columns || !data?.state?.rows || !data?.state?.cells) {
        console.error("No data to export.");
        return;
      }
  
      // The data is already in the correct format, so we can send it as is
      const preparedData = {
        columns: data.state.columns,
        rows: data.state.rows,
        cells: data.state.cells
      };
  
      console.log('Data being sent to API:', preparedData);
  
      try {
        await apiExportTriples(preparedData);
      } catch (error) {
        console.error('Error exporting triples:', error);
      }
    };
  
    return (
      <Button leftSection={<IconShare />} onClick={handleExportTriples}>
        Export to Triples
      </Button>
    );
  };