import { ReactNode } from "react";
import { ActionIcon, ActionIconProps, Tooltip } from "@mantine/core";
import { IconInfoCircle } from "@tabler/icons-react";

interface InfoProps extends ActionIconProps {
  children: ReactNode;
}

export function Info({ children, ...props }: InfoProps) {
  return (
    <Tooltip label={children}>
      <ActionIcon color="blue" variant="transparent" {...props}>
        <IconInfoCircle />
      </ActionIcon>
    </Tooltip>
  );
}
