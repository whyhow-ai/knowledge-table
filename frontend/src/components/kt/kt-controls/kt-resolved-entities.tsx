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
  Divider
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { IconReplace } from "@tabler/icons-react";
import { isEmpty } from "lodash-es";
import { useStore } from "@config/store";

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

      <Modal
        size="xl"
        title="Resolved entities"
        opened={opened}
        onClose={handlers.close}
      >
        {resolvedEntities && !isEmpty(resolvedEntities) ? (
          <Stack>
            <Text size="sm">The following entities were resolved in the last answer:</Text>
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
            
            <Divider />
            
            <Text size="sm" fw={500}>Full answer with resolved entities:</Text>
            <Paper withBorder p="md">
              <Text>{resolvedEntities[0]?.fullAnswer}</Text>
            </Paper>
          </Stack>
        ) : (
          <Text>No resolved entities available.</Text>
        )}
      </Modal>
    </Group>
  );
}