import {
  Button,
  Modal,
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
import { isEmpty } from "lodash-es";
import { useStore } from "@config/store";

export function KtResolvedEntities(props: BoxProps) {
  const [opened, handlers] = useDisclosure(false);
  const resolvedEntities = useStore(state => state.getTable().resolvedEntities);
  
  console.log('Resolved Entities:', resolvedEntities);
  console.log('Is Array:', Array.isArray(resolvedEntities));
  console.log('Is Empty:', isEmpty(resolvedEntities));

  return (
    <Group gap={8} {...props}>
      <Button
        variant="light"
        leftSection={<IconReplace size={16} />}
        onClick={handlers.open}
      >
        Resolved entities
      </Button>

      <Modal
        size="xl"
        title="Resolved entities"
        opened={opened}
        onClose={handlers.close}
      >
        {resolvedEntities && Array.isArray(resolvedEntities) && resolvedEntities.length > 0 ? (
          <Stack>
            <Text size="sm">The following transformations were applied:</Text>
            <Paper withBorder p="md">
              <List spacing="xs">
                {resolvedEntities.map(({ original, resolved }, index) => (
                  <List.Item key={index}>
                    <Group>
                      <Code>{original}</Code>
                      <Text span>→</Text>
                      <Code>{resolved}</Code>
                    </Group>
                  </List.Item>
                ))}
              </List>
            </Paper>
          </Stack>
        ) : (
          <Text>No transformations available.</Text>
        )}
      </Modal>
    </Group>
  );
}