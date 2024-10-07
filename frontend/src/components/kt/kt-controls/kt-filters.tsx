import {
  BoxProps,
  Button,
  Popover,
  Divider,
  Group,
  ActionIcon,
  Select,
  TextInput,
  Paper,
  Text,
  Anchor
} from "@mantine/core";
import { IconFilter, IconPlus, IconTrash } from "@tabler/icons-react";
import { isEmpty, debounce } from "lodash-es";
import { AnswerTableFilter, useStore } from "@config/store";
import { Empty } from "@components";
import { plur } from "@utils/functions";

export function KtFilters(props: BoxProps) {
  const filters = useStore(store => store.filters);
  const columns = useStore(store => store.columns);

  const handleAdd = () => {
    useStore.getState().addFilter({
      columnId: columns[0]?.id ?? "",
      criteria: "contains",
      value: ""
    });
  };

  return (
    <Group {...props}>
      <Popover position="bottom-start">
        <Popover.Target>
          <Button leftSection={<IconFilter />}>Filters</Button>
        </Popover.Target>
        <Popover.Dropdown w={540} p="sm">
          {isEmpty(filters) ? (
            <Empty message="No filters are applied" />
          ) : (
            filters.map(filter => (
              <Group key={filter.id} mb="xs" gap="xs" wrap="nowrap">
                <Select
                  variant="unstyled"
                  data={columns.map(column => ({
                    value: column.id,
                    label: column.prompt.entityType
                  }))}
                  comboboxProps={{ withinPortal: false }}
                  defaultValue={filter.columnId}
                  onChange={columnId =>
                    columnId && debouncedEditFilter(filter.id, { columnId })
                  }
                />
                <Select
                  data={criteriaOptions}
                  comboboxProps={{ withinPortal: false }}
                  defaultValue={filter.criteria}
                  onChange={criteria =>
                    criteria &&
                    debouncedEditFilter(filter.id, {
                      criteria: criteria as AnswerTableFilter["criteria"]
                    })
                  }
                />
                <TextInput
                  placeholder="Value"
                  defaultValue={filter.value}
                  onChange={e =>
                    debouncedEditFilter(filter.id, { value: e.target.value })
                  }
                />
                <ActionIcon
                  color="red"
                  onClick={() => useStore.getState().deleteFilters([filter.id])}
                >
                  <IconTrash />
                </ActionIcon>
              </Group>
            ))
          )}
          <Divider mt="xs" />
          <Group mt="xs">
            <Button flex={1} leftSection={<IconPlus />} onClick={handleAdd}>
              Add filter
            </Button>
            <Button
              flex={1}
              color="red"
              variant="light"
              leftSection={<IconTrash />}
              onClick={() => useStore.getState().deleteFilters()}
            >
              Clear
            </Button>
          </Group>
        </Popover.Dropdown>
      </Popover>
      {!isEmpty(filters) && (
        <Paper withBorder py={4} px="xs">
          <Group>
            <Text>
              {filters.length} {plur("cell", filters)} filters
            </Text>
            <Anchor onClick={useStore.getState().applyFilters}>Reapply</Anchor>
          </Group>
        </Paper>
      )}
    </Group>
  );
}

// Utils

const criteriaOptions: Array<{
  value: AnswerTableFilter["criteria"];
  label: string;
}> = [
  { value: "contains", label: "Contains" },
  { value: "contains_not", label: "Does not contain" }
];

const debouncedEditFilter = debounce(useStore.getState().editFilter, 500);
