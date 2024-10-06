import { ReactNode } from "react";
import { Box, BoxProps, Center, Group, Text } from "@mantine/core";
import { IconDatabaseOff } from "@tabler/icons-react";

interface Props extends BoxProps {
  message: ReactNode;
  messageExtra?: ReactNode;
}

export function Empty({ message, messageExtra, ...props }: Props) {
  return (
    <Center ta="center" {...props}>
      <Box>
        <IconDatabaseOff size={40} opacity={0.2} />
        <Group mt="sm" justify="center">
          {messageExtra}
          <Text c="dimmed">{message}</Text>
        </Group>
      </Box>
    </Center>
  );
}
