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
import { useMemo } from 'react';
import { ResolvedEntity } from '@config/store/store.types';

export function KtResolvedEntities(props: BoxProps) {
  const [opened, handlers] = useDisclosure(false);
  const table = useStore(state => state.getTable());
  const editActiveTable = useStore(state => state.editActiveTable);

  const allResolvedEntities = useMemo(() => {
    const globalEntities = table.globalRules.flatMap(rule => rule.resolvedEntities || []);
    const columnEntities = table.columns.flatMap(column => column.resolvedEntities || []);
    return [...globalEntities, ...columnEntities];
  }, [table.globalRules, table.columns]);

  const handleUndoTransformation = (entity: ResolvedEntity) => {
    const rows = table.rows.map(row => ({
      ...row,
      cells: Object.fromEntries(
        Object.entries(row.cells).map(([columnId, cellValue]) => {
          if (typeof cellValue === 'string' && cellValue.includes(entity.fullAnswer)) {
            return [columnId, cellValue.replace(entity.fullAnswer, entity.original)];
          }
          return [columnId, cellValue];
        })
      )
    }));
  
    // If no source information, assume it's a column entity
    const source = entity.source || { type: 'column' as const, id: table.columns[0].id };
  
    if (source.type === 'global') {
      const globalRules = table.globalRules.map(rule => 
        rule.id === source.id ? {
          ...rule,
          resolvedEntities: (rule.resolvedEntities || []).filter(e => e.original !== entity.original)
        } : rule
      );
      editActiveTable({ rows, globalRules });
    } else {
      const columns = table.columns.map(column =>
        column.id === source.id ? {
          ...column,
          resolvedEntities: (column.resolvedEntities || []).filter(e => e.original !== entity.original)
        } : column
      );
      editActiveTable({ rows, columns });
    }
  };

  return (
    <Group gap={8} {...props}>
      <Button leftSection={<IconReplace size={16} />} onClick={handlers.open}>
        Resolved entities
      </Button>

      <Drawer position="right" size="md" title="Resolved entities" opened={opened} onClose={handlers.close}>
        {allResolvedEntities.length > 0 ? (
          <Stack>
            <Text size="sm">The following transformations were applied:</Text>
            <Paper withBorder p="md">
              <List spacing="xs">
                {allResolvedEntities.map((entity, index) => (
                  <List.Item key={index}>
                    <Group justify="space-between" wrap="nowrap">
                      <Group gap="xs">
                        <Code>{entity.original}</Code>
                        <Text span>→</Text>
                        <Code>{entity.fullAnswer}</Code>
                      </Group>
                      <Tooltip label="Undo transformation">
                        <ActionIcon
                          variant="subtle"
                          color="red"
                          onClick={() => handleUndoTransformation(entity)}
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