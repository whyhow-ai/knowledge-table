import { BoxProps } from "@mantine/core";
import { KtPromptSettings } from "../kt-prompt-settings";
import { AnswerTableColumn, useStore } from "@config/store";

interface Props extends BoxProps {
  column: AnswerTableColumn;
  lastColumn: boolean;
}

export function KtColumnDropdown({ column, lastColumn, ...props }: Props) {
  return (
    <KtPromptSettings
      value={column.prompt}
      onChange={value => useStore.getState().editColumn(column.id, value)}
      onRerun={() => useStore.getState().rerunColumn(column.id)}
      onUnwind={
        lastColumn
          ? () => useStore.getState().unwindColumn(column.id)
          : undefined
      }
      onHide={() => useStore.getState().toggleColumn(column.id, true)}
      onDelete={() => useStore.getState().deleteColumns([column.id])}
      {...props}
    />
  );
}
