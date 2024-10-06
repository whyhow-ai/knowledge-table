import {
  ActionIcon,
  BoxProps,
  HoverCard,
  Pill,
  Table,
  Text,
  Tooltip
} from "@mantine/core";
import { IconEye } from "@tabler/icons-react";
import { shallow } from "zustand/shallow";
import { isEmpty } from "lodash-es";
import { useStore } from "@config/store";

export function KtHiddenPill(props: BoxProps) {
  const hiddenColumns = useStore(
    store => store.columns.filter(column => column.hidden),
    shallow
  );

  return isEmpty(hiddenColumns) ? null : (
    <HoverCard>
      <HoverCard.Target>
        <Pill {...props}>{hiddenColumns.length} hidden</Pill>
      </HoverCard.Target>
      <HoverCard.Dropdown w={350} px={0}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Hidden column</Table.Th>
              <Table.Th w={1}>
                <Tooltip label="Show all columns">
                  <ActionIcon
                    onClick={() => useStore.getState().toggleAllColumns(false)}
                  >
                    <IconEye />
                  </ActionIcon>
                </Tooltip>
              </Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {hiddenColumns.map(column => (
              <Table.Tr key={column.id}>
                <Table.Td>
                  <Text lineClamp={1}>{column.prompt.query}</Text>
                </Table.Td>
                <Table.Td>
                  <Tooltip label="Show column">
                    <ActionIcon
                      onClick={() =>
                        useStore.getState().toggleColumn(column.id, false)
                      }
                    >
                      <IconEye />
                    </ActionIcon>
                  </Tooltip>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      </HoverCard.Dropdown>
    </HoverCard>
  );
}
