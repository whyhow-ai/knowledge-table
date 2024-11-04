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
    
    // Only show entities where a transformation was actually applied
    return entities.filter(entity => {
      // For arrays, compare stringified versions
      if (Array.isArray(entity.original) && Array.isArray(entity.resolved)) {
        return JSON.stringify(entity.original) !== JSON.stringify(entity.resolved);
      }
      // For strings, direct comparison
      return entity.original !== entity.resolved;
    });
  }, [table.globalRules, table.columns]);

  const handleUndoTransformation = (entity: ResolvedEntity) => {
    const rows = table.rows.map(row => ({
      ...row,
      cells: Object.fromEntries(
        Object.entries(row.cells).map(([columnId, cellValue]) => {
          // Only modify cells in the source column or if it's a global rule
          if (entity.source.type === 'column' && columnId !== entity.source.id) {
            return [columnId, cellValue];
          }
  
          // Check if values match (either both arrays or both strings)
          const valuesMatch = Array.isArray(cellValue) && Array.isArray(entity.resolved) 
            ? JSON.stringify(cellValue) === JSON.stringify(entity.resolved)
            : cellValue === entity.resolved;
  
          // If they match, replace with original value
          if (valuesMatch) {
            return [columnId, entity.original];
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
      <Button 
        leftSection={<IconReplace size={16} />} 
        onClick={handlers.open}
        disabled={allResolvedEntities.length === 0}
        variant="light"  // Always light variant
      >
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
                        <Code block style={{ whiteSpace: 'pre-wrap' }}>
                          {Array.isArray(entity.original) 
                            ? entity.original.join('\n')  // One item per line
                            : entity.original}
                        </Code>
                        <Text size="sm" fw={500}>To:</Text>
                        <Code block style={{ whiteSpace: 'pre-wrap' }}>
                          {Array.isArray(entity.resolved)
                            ? entity.resolved.join('\n')  // One item per line
                            : entity.resolved}
                        </Code>
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