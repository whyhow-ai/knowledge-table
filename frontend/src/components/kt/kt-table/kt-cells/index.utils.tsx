import { ReactNode } from "react";
import { Box, Popover, ScrollArea } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { Wrap } from "@components";
import { cn } from "@utils/functions";
import classes from "./index.module.css";

interface CellPopoverProps {
  monoClick?: boolean;
  mainAxisOffset?: number;
  target: ReactNode;
  dropdown: ReactNode;
  scrollable?: boolean;
}

export function CellPopover({
  monoClick,
  mainAxisOffset = 1,
  target,
  dropdown,
  scrollable
}: CellPopoverProps) {
  const [opened, handlers] = useDisclosure(false);
  return (
    <Popover
      opened={opened}
      onClose={handlers.close}
      offset={{ mainAxis: mainAxisOffset, crossAxis: -1 }}
      width="target"
      position="bottom-start"
      transitionProps={{ transition: "scale-y" }}
    >
      <Popover.Target>
        <Box
          className={cn(classes.target, opened && classes.active)}
          {...(monoClick
            ? { onClick: handlers.open }
            : { onDoubleClick: handlers.open })}
        >
          {target}
        </Box>
      </Popover.Target>
      <Popover.Dropdown
        onPointerDown={e => e.stopPropagation()}
        onKeyDown={e => e.stopPropagation()}
        className={classes.dropdown}
      >
        <Wrap
          with={
            scrollable &&
            (node => (
              <ScrollArea.Autosize mah={500}>{node}</ScrollArea.Autosize>
            ))
          }
        >
          <Box p="sm">{dropdown}</Box>
        </Wrap>
      </Popover.Dropdown>
    </Popover>
  );
}
