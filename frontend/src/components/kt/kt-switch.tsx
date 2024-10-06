import { Text, BoxProps, Button, Group, Menu } from "@mantine/core";
import { IconChevronDown, IconChevronsRight } from "@tabler/icons-react";

export function KtSwitch(props: BoxProps) {
  return (
    <Group gap="xs" {...props}>
      <Text>Knowledge Table</Text>
      <IconChevronsRight size={16} opacity={0.8} />
      <Menu width="target">
        <Menu.Target>
          <Button rightSection={<IconChevronDown />}>Current table</Button>
        </Menu.Target>
        <Menu.Dropdown>
          <Menu.Item>Table 1</Menu.Item>
          <Menu.Item>Table 2</Menu.Item>
          <Menu.Item>Table 3</Menu.Item>
        </Menu.Dropdown>
      </Menu>
    </Group>
  );
}
