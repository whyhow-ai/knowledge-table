import { Cell, CellTemplate, Compatible, Uncertain } from "@silevis/reactgrid";
import { useMutation } from "@tanstack/react-query";
import {
  Group,
  Text,
  ActionIcon,
  Tooltip,
  Divider,
  List,
  Button,
  FileButton,
  Loader
} from "@mantine/core";
import {
  IconFileText,
  IconPlus,
  IconRefresh,
  IconTrash,
  IconUpload
} from "@tabler/icons-react";
import { CellPopover } from "./index.utils";
import { AnswerTableRow, useStore } from "@config/store";

export interface KtRowCell extends Cell {
  type: "kt-row";
  row: AnswerTableRow;
}

export class KtRowCellTemplate implements CellTemplate<KtRowCell> {
  getCompatibleCell(cell: Uncertain<KtRowCell>): Compatible<KtRowCell> {
    if (cell.type !== "kt-row" || !cell.row) {
      throw new Error("Invalid cell type");
    }
    return {
      ...cell,
      type: "kt-row",
      row: cell.row,
      text: cell.row.sourceData?.document.name ?? "",
      value: NaN
    };
  }

  isFocusable() {
    return false;
  }

  render({ row }: Compatible<KtRowCell>) {
    return <Content row={row} />;
  }
}

function Content({ row }: { row: AnswerTableRow }) {
  const { mutateAsync: handleFillRow, isPending: isFillingRow } = useMutation({
    mutationFn: ({ id, file }: { id: string; file: File }) =>
      useStore.getState().fillRow(id, file)
  });

  const handleRerun = () => {
    useStore.getState().rerunRows([row.id]);
  };

  const handleDelete = () => {
    useStore.getState().deleteRows([row.id]);
  };

  if (!row.sourceData) {
    return (
      <CellPopover
        monoClick
        target={
          <Group h="100%" pl="xs" gap="xs" wrap="nowrap">
            {isFillingRow ? (
              <Loader size="xs" />
            ) : (
              <IconPlus size={18} opacity={0.4} />
            )}
            <Text c="dimmed">Add data</Text>
          </Group>
        }
        dropdown={
          <>
            <FileButton
              accept="application/pdf,text/plain"
              onChange={file => file && handleFillRow({ id: row.id, file })}
            >
              {fileProps => (
                <Button
                  {...fileProps}
                  leftSection={
                    isFillingRow ? <Loader size="xs" /> : <IconUpload />
                  }
                >
                  Upload document
                </Button>
              )}
            </FileButton>
            <Text mt="xs" size="xs" c="dimmed">
              Accepted formats: pdf, txt
            </Text>
          </>
        }
      />
    );
  }

  if (row.sourceData.type === "document") {
    return (
      <CellPopover
        target={
          <Group h="100%" pl="xs" gap="xs" wrap="nowrap">
            <IconFileText size={18} opacity={0.7} />
            <Text fw={500}>{row.sourceData?.document.name}</Text>
          </Group>
        }
        dropdown={
          <>
            <Group gap="xs" justify="space-between">
              <Text fw={500}>{row.sourceData.document.name}</Text>
              <Group gap="xs">
                <Tooltip label="Rerun row">
                  <ActionIcon onClick={handleRerun}>
                    <IconRefresh />
                  </ActionIcon>
                </Tooltip>
                <Tooltip label="Delete row">
                  <ActionIcon color="red" onClick={handleDelete}>
                    <IconTrash />
                  </ActionIcon>
                </Tooltip>
              </Group>
            </Group>
            <Divider mt="xs" mx="calc(var(--mantine-spacing-sm) * -1)" />
            <List mt="xs">
              <List.Item>
                <b>Type</b>: Document
              </List.Item>
              <List.Item>
                <b>Tag</b>: {row.sourceData.document.tag}
              </List.Item>
              <List.Item>
                <b>Author</b>: {row.sourceData.document.author}
              </List.Item>
              <List.Item>
                <b>Page count</b>: {row.sourceData.document.page_count}
              </List.Item>
            </List>
          </>
        }
      />
    );
  }
}
