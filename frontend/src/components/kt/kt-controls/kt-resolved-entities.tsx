import {
  Button,
  Group,
  Text,
  Code,
  Paper,
  BoxProps,
  Stack,
  List,
  ActionIcon,
  Tooltip,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconReplace, IconX } from "@tabler/icons-react";
import { useStore } from "@config/store";
import { Drawer } from '@mantine/core'; 

export function KtResolvedEntities(props: BoxProps) {
  const [opened, handlers] = useDisclosure(false);
  const table = useStore(state => state.getTable());
  const editActiveTable = useStore(state => state.editActiveTable);
  const resolvedEntities = table.resolvedEntities;

  const handleUndoTransformation = (original: string, transformed: string) => {
    // Get all rows
    const rows = [...table.rows];
    
    // For each row, check all cells and replace the transformed text back to original
    const updatedRows = rows.map(row => ({
      ...row,
      cells: Object.fromEntries(
        Object.entries(row.cells).map(([columnId, cellValue]) => {
          if (typeof cellValue === 'string' && cellValue.includes(transformed)) {
            return [columnId, cellValue.replace(transformed, original)];
          }
          return [columnId, cellValue];
        })
      )
    }));

    // Update the table with the new rows and remove this transformation from resolvedEntities
    editActiveTable({
      rows: updatedRows,
      resolvedEntities: resolvedEntities?.filter(
        entity => entity.original !== original
      )
    });
  };

  return (
    <Group gap={8} {...props}>
      <Button
        leftSection={<IconReplace size={16} />}
        onClick={handlers.open}
      >
        Resolved entities
      </Button>

      <Drawer
        position="right"
        size="md"
        title="Resolved entities"
        opened={opened}
        onClose={handlers.close}
      >
        {resolvedEntities && resolvedEntities.length > 0 ? (
          <Stack>
            <Text size="sm">The following transformations were applied:</Text>
            <Paper withBorder p="md">
              <List spacing="xs">
                {resolvedEntities.map(({ original, fullAnswer }, index) => (
                  <List.Item key={index}>
                    <Group justify="space-between" wrap="nowrap">
                      <Group gap="xs">
                        <Code>{String(original)}</Code>
                        <Text span>→</Text>
                        <Code>{String(fullAnswer)}</Code>
                      </Group>
                      <Tooltip label="Undo transformation">
                        <ActionIcon
                          variant="subtle"
                          color="red"
                          onClick={() => handleUndoTransformation(original, fullAnswer)}
                          size="sm"
                        >
                          <IconX size={16} />
                        </ActionIcon>
                      </Tooltip>
                    </Group>
                  </List.Item>
                ))}
              </List>
            </Paper>
          </Stack>
        ) : (
          <Text>No transformations available.</Text>
        )}
      </Drawer>
    </Group>
  );
}