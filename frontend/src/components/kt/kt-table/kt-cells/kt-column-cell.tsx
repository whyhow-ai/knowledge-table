import { Cell, CellTemplate, Compatible, Uncertain } from "@silevis/reactgrid";
import { Group, Text, ColorSwatch } from "@mantine/core";
import { CellPopover } from "./index.utils";
import { KtColumnSettings } from "./kt-column-settings";
import { AnswerTableColumn, useStore } from "@config/store";
import { entityColor } from "@utils/functions";

export interface KtColumnCell extends Cell {
  type: "kt-column";
  column: AnswerTableColumn;
}

export class KtColumnCellTemplate implements CellTemplate<KtColumnCell> {
  getCompatibleCell(cell: Uncertain<KtColumnCell>): Compatible<KtColumnCell> {
    if (cell.type !== "kt-column" || !cell.column) {
      throw new Error("Invalid cell type");
    }
    return {
      ...cell,
      type: "kt-column",
      column: cell.column,
      text: cell.column.entityType,
      value: NaN
    };
  }

  isFocusable() {
    return false;
  }

  render({ column }: Compatible<KtColumnCell>) {
    return (
      <CellPopover
        monoClick={!column.entityType.trim()}
        mainAxisOffset={0}
        target={
          <Group h="100%" pl="xs" gap="xs" wrap="nowrap">
            <ColorSwatch
              size={12}
              color={entityColor(column.entityType).fill}
            />
            <Text fw={500}>{column.entityType}</Text>
          </Group>
        }
        dropdown={
          <KtColumnSettings
            value={column}
            onChange={(value, run) => {
              useStore.getState().editColumn(column.id, value);
              run && useStore.getState().rerunColumns([column.id]);
            }}
            onRerun={() => useStore.getState().rerunColumns([column.id])}
            onUnwind={() => useStore.getState().unwindColumn(column.id)}
            onHide={() =>
              useStore.getState().editColumn(column.id, { hidden: true })
            }
            onDelete={() => useStore.getState().deleteColumns([column.id])}
          />
        }
      />
    );
  }
}
