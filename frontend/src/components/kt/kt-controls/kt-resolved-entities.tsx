import {
  Button,
  Group,
  Text,
  Code,
  Paper,
  BoxProps,
  Stack,
  List,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconReplace } from "@tabler/icons-react";
import { useStore } from "@config/store";
import { Drawer } from '@mantine/core'; 

export function KtResolvedEntities(props: BoxProps) {
  const [opened, handlers] = useDisclosure(false);
  const resolvedEntities = useStore(state => state.getTable().resolvedEntities);

  return (
    <Group gap={8} {...props}>
      <Button
        variant="light"
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
                    <Group>
                      <Code>{String(original)}</Code>
                      <Text span>→</Text>
                      <Code>{String(fullAnswer)}</Code>
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