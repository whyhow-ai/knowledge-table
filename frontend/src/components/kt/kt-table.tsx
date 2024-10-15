import { useRef } from "react";
import {
  BoxProps,
  Group,
  Text,
  ScrollArea,
  Loader,
  ColorSwatch
} from "@mantine/core";
import { IconFileText, IconPlus } from "@tabler/icons-react";
import { shallow } from "zustand/shallow";
import {
  formatAnswer,
  KtAdderDropdown,
  KtCellDropdown,
  KtColumnDropdown,
  KtRowDropdown
} from "./kt-dropdown";
import { KtFileUploadButton } from "./kt-file-upload-button";
import { useStore } from "@config/store";
import { DataGrid, DragResizer } from "@components";
import { entityColor } from "@utils/functions";

export function KtTable(props: BoxProps) {
  const ref = useRef<HTMLButtonElement>(null);
  const columns = useStore(
    store => store.columns.filter(column => !column.hidden),
    shallow
  );
  const rows = useStore(
    store => store.rows.filter(row => !row.hidden),
    shallow
  );
  const cells = useStore(store => store.cells);
  const selection = useStore(store => store.selection);

  return (
    <ScrollArea {...props}>
      <DataGrid
        mb="md"
        columns={columns.map((column, index) => ({
          key: column.id,
          width: column.width,
          content: (
            <>
              <Group wrap="nowrap">
                <ColorSwatch
                  size={12}
                  color={entityColor(column.prompt.entityType).fill}
                />
                <Text fw={500}>{column.prompt.entityType}</Text>
              </Group>
              <DragResizer
                position="right"
                value={column.width}
                onChange={width =>
                  useStore.getState().resizeColumn(column.id, width)
                }
              />
            </>
          ),
          dropdown: {
            content: (
              <KtColumnDropdown
                column={column}
                lastColumn={index === columns.length - 1}
              />
            )
          }
        }))}
        rows={rows.map(row => ({
          key: row.id,
          width: 260,
          content: (
            <Group wrap="nowrap">
              <IconFileText size={18} opacity={0.7} />
              <Text fw={500}>{row.document.name}</Text>
            </Group>
          ),
          dropdown: {
            content: <KtRowDropdown row={row} />
          }
        }))}
        cells={cells.map(cell => ({
          key: `${cell.rowId}-${cell.columnId}`,
          groupKey: cell.answer.id,
          content: formatAnswer(cell.answer),
          dropdown: {
            scrollable: true,
            content: <KtCellDropdown cell={cell} />
          }
        }))}
        extraColumn={{
          width: 160,
          content: (
            <Group h="100%">
              <IconPlus size={18} opacity={0.7} />
              <Text fw={500}>Add question</Text>
            </Group>
          ),
          dropdown: {
            content: <KtAdderDropdown />
          }
        }}
        extraRow={{
          onClick: () => ref.current?.click(),
          content: <KtFileUploadButton ref={ref} display="none" />
        }}
        defaultCell={() => ({
          content: <Loader size="xs" />
        })}
        selection={selection}
        onSelectionChange={selection => useStore.setState({ selection })}
      />
    </ScrollArea>
  );
}
