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
    const entities = [...globalEntities, ...columnEntities];
    return entities;
  }, [table.globalRules, table.columns]);

  // Helper to format display value based on type
  const getDisplayValue = (value: string, entity: ResolvedEntity, isOriginal: boolean) => {
    try {
      const parsed = JSON.parse(value);
      if (Array.isArray(parsed)) {
        if (isOriginal) {
          
          return (
            <Code block style={{ whiteSpace: 'pre-wrap' }}>
              {parsed
                .map(item => {
                  // Check if the item contains the resolved value
                  const shouldReplace = item.includes(entity.resolved);
                  // If it contains the resolved value, replace that part with the original
                  return shouldReplace ? item.replace(entity.resolved, entity.original) : item;
                })
                .join('\n')}
            </Code>
          );
        } else {
          // For "To": Show fullAnswer as is
          return (
            <Code block style={{ whiteSpace: 'pre-wrap' }}>
              {parsed.join('\n')}
            </Code>
          );
        }
      }
    } catch {
      // If not an array, show the original value for "From" or the value as is for "To"
      return (
        <Code block style={{ whiteSpace: 'pre-wrap' }}>
          {isOriginal ? entity.original : value}
        </Code>
      );
    }
  };

  const handleUndoTransformation = (entity: ResolvedEntity) => {
    const rows = table.rows.map(row => ({
      ...row,
      cells: Object.fromEntries(
        Object.entries(row.cells).map(([columnId, cellValue]) => {
          if (typeof cellValue === 'string') {
            // Replace resolved with original in string values
            return [columnId, cellValue.includes(entity.resolved) 
              ? cellValue.replace(entity.resolved, entity.original) 
              : cellValue];
          } else if (Array.isArray(cellValue)) {
            // Replace resolved with original in array values
            return [
              columnId, 
              cellValue.map(item => 
                typeof item === 'string' && item.includes(entity.resolved)
                  ? item.replace(entity.resolved, entity.original)
                  : item
              )
            ];
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
              <List spacing="md">
                {allResolvedEntities.map((entity, index) => (
                  <List.Item key={index}>
                    <Group justify="space-between" align="flex-start" wrap="nowrap">
                      <Stack gap="xs" style={{ flex: 1 }}>
                        <Text size="sm" fw={500}>From:</Text>
                        {getDisplayValue(entity.fullAnswer, entity, true)}
                        <Text size="sm" fw={500}>To:</Text>
                        {getDisplayValue(entity.fullAnswer, entity, false)}
                        </Stack>
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