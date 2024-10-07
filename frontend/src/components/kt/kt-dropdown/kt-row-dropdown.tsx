import { useMutation } from "@tanstack/react-query";
import {
  BoxProps,
  Box,
  Group,
  Text,
  ActionIcon,
  Tooltip,
  Divider,
  List
} from "@mantine/core";
import { IconReload, IconTrash } from "@tabler/icons-react";
import { AnswerTableRow, useStore } from "@config/store";

interface Props extends BoxProps {
  row: AnswerTableRow;
}

export function KtRowDropdown({ row, ...props }: Props) {
  const { mutateAsync: handleDelete, isPending } = useMutation({
    mutationFn: useStore.getState().deleteRows
  });

  const handleRerun = () => {
    useStore.getState().rerunRow(row.id);
  };

  return (
    <Box {...props}>
      <Group gap="xs" justify="space-between">
        <Text fw={500}>{row.document.name}</Text>
        <Group gap="xs">
          <Tooltip label="Rerun row">
            <ActionIcon onClick={handleRerun}>
              <IconReload />
            </ActionIcon>
          </Tooltip>
          <Tooltip label="Delete row">
            <ActionIcon
              color="red"
              loading={isPending}
              onClick={() => handleDelete([row.id])}
            >
              <IconTrash />
            </ActionIcon>
          </Tooltip>
        </Group>
      </Group>
      <Divider mt="xs" mx="calc(var(--mantine-spacing-sm) * -1)" />
      <List mt="xs">
        <List.Item>
          <b>Tag</b>: {row.document.tag}
        </List.Item>
        <List.Item>
          <b>Author</b>: {row.document.author}
        </List.Item>
        <List.Item>
          <b>Page count</b>: {row.document.page_count}
        </List.Item>
      </List>
    </Box>
  );
}
