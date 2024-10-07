import { ReactNode } from "react";
import {
  Box,
  BoxProps,
  Group,
  Input,
  Menu,
  MenuDropdownProps,
  MenuProps
} from "@mantine/core";
import { IconChevronRight } from "@tabler/icons-react";
import { cn } from "@utils/functions";
import classes from "./index.module.css";

interface Props extends BoxProps {
  disabled?: boolean;
  label: ReactNode;
  rightSection?: ReactNode;
  menu?: ReactNode;
  menuProps?: MenuProps;
  dropdownProps?: MenuDropdownProps;
}

export function MenuButton({
  label,
  rightSection,
  disabled,
  menu,
  menuProps,
  dropdownProps,
  ...props
}: Props) {
  return (
    <Menu
      position="right-start"
      offset={2}
      withinPortal={false}
      disabled={disabled}
      {...menuProps}
    >
      <Menu.Target>
        <Box {...props} className={cn(classes.menuButton, props.className)}>
          <Input.Label>{label}</Input.Label>
          <Group>
            <Box>{rightSection}</Box>
            <IconChevronRight size={16} />
          </Group>
        </Box>
      </Menu.Target>
      <Menu.Dropdown {...dropdownProps}>{menu}</Menu.Dropdown>
    </Menu>
  );
}
