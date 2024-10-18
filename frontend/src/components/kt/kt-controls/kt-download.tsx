import { Button } from "@mantine/core";
import { IconDownload, IconShare } from "@tabler/icons-react";
import { isArray, pick } from "lodash-es";
import { useStore } from "@config/store";
import { exportTriples } from "@config/api";
import { download } from "@utils/functions";

export const KtDownload = {
  Csv: () => {
    const handleDownload = () => {
      const data = useStore.getState();
      const columns = data.columns.map(
        col => col.prompt.entityType || "Unknown"
      );

      let csvData = `Document,${columns.join(",")}\n`;
      const cellMap = data._getCellMap();

      for (const row of data.rows) {
        const documentName = row.document.name || "Unknown";

        const cellValues = data.columns.map(col => {
          const cell = cellMap.get(`${row.id}-${col.id}`);
          if (!cell) return "";
          const answer = cell.answer.answer;
          if (answer === null) {
            return "";
          } else if (isArray(answer)) {
            return `"${answer.join(", ")}"`;
          } else {
            return String(answer);
          }
        });

        csvData += `"${documentName}",${cellValues.join(",")}\n`;
      }

      download("knowledge-table-data.csv", {
        mimeType: "text/csv",
        content: csvData
      });
    };

    return (
      <Button leftSection={<IconDownload />} onClick={handleDownload}>
        Download CSV
      </Button>
    );
  },

  Triples: () => {
    const handleExport = async () => {
      const data = pick(useStore.getState(), ["columns", "rows", "cells"]);
      const blob = await exportTriples(data);
      download("triples.json", blob);
    };

    return (
      <Button leftSection={<IconShare />} onClick={handleExport}>
        Export to Triples
      </Button>
    );
  }
};
