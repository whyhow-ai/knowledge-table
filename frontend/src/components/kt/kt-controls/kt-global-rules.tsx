import {
  Button,
  Modal,
  Divider,
  Group,
  ActionIcon,
  Select,
  NumberInput,
  TagsInput,
  TextInput,
  Text,
  Box,
  Code,
  Paper,
  BoxProps,
  Table
} from "@mantine/core";
import { Dropzone } from "@mantine/dropzone";
import { useDisclosure } from "@mantine/hooks";
import {
  IconFile,
  IconGavel,
  IconPlus,
  IconTrash,
  IconUpload,
  IconX
} from "@tabler/icons-react";
import { isString, cloneDeep, isNaN, isEmpty } from "lodash-es";
import csv from "csvtojson";
import { z } from "zod";
import {
  useStore,
  AnswerTableRule,
  defaultRules,
  ruleOptions,
  ruleInfo
} from "@config/store";
import { Info } from "@components";
import { niceTry, plur } from "@utils/functions";

export function KTGlobalRules(props: BoxProps) {
  const [opened, handlers] = useDisclosure(false);
  const rules = useStore(state => state.getTable().globalRules);

  const handleDrop = async (files: File[]) => {
    for (const file of files) {
      const text = await file.text();
      const json = await csv().fromString(text);
      niceTry(() => {
        const parsed = csvJsonSchema.parse(json);
        useStore.getState().addGlobalRules(
          parsed.map(rule => {
            const args: Partial<AnswerTableRule> =
              rule.rule_type === "max_length"
                ? { length: safeInt(rule.value) }
                : { options: rule.value.split(",") };
            return {
              entityType: rule.entity_type ?? "",
              type: rule.rule_type,
              ...args
            };
          })
        );
      });
    }
  };

  const handleAddRule = () => {
    useStore
      .getState()
      .addGlobalRules([{ entityType: "", type: "must_return", options: [] }]);
  };

  const handleRuleTypeChange = (id: string, type: AnswerTableRule["type"]) => {
    useStore.getState().editGlobalRule(id, cloneDeep(defaultRules[type]));
  };

  return (
    <Group gap={8} {...props}>
      <Button leftSection={<IconGavel />} onClick={handlers.open}>
        Global rules
      </Button>
      <Modal
        size="xl"
        title="Global rules"
        opened={opened}
        onClose={handlers.close}
      >
        <Dropzone mb="md" accept={["text/csv"]} onDrop={handleDrop}>
          <Group
            justify="center"
            gap="xl"
            mih={210}
            style={{ pointerEvents: "none" }}
          >
            <Dropzone.Accept>
              <Box component={IconUpload} c="blue" size={48} />
            </Dropzone.Accept>
            <Dropzone.Reject>
              <Box component={IconX} c="red" size={48} />
            </Dropzone.Reject>
            <Dropzone.Idle>
              <Box component={IconFile} c="dimmed" size={48} />
            </Dropzone.Idle>
            <Box>
              <Text size="xl" inline>
                Drag and drop a rules CSV file here
              </Text>
              <Text size="sm" c="dimmed" inline mt={7}>
                Expected CSV columns: <Code>rule_type</Code>
                <Text span inline c="red">
                  *
                </Text>{" "}
                <Code>value</Code>
                <Text span inline c="red">
                  *
                </Text>{" "}
                <Code>entity_type</Code>. Sample:
              </Text>
              <Code mt="xs" block>
                rule_type,value,entity_type
                <br />
                may_return,"hot,cold",Temperature
                <br />
                must_return,"red,blue,green",Color
                <br />
                max_length,3,
                <br />
                resolve_entity,"blue:ultramarine,red:crimson",Color
              </Code>
            </Box>
          </Group>
        </Dropzone>
        {!isEmpty(rules) && (
          <Table w="100%" highlightOnHover style={{ tableLayout: "fixed" }}>
            <Table.Thead>
              <Table.Tr>
                <Table.Th w="99%">Entity type</Table.Th>
                <Table.Th w="99%">Rule type</Table.Th>
                <Table.Th w="99%">Value</Table.Th>
                <Table.Th w={80} />
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {rules.map((rule, index) => (
                <Table.Tr key={index}>
                  <Table.Td>
                    <TextInput
                      variant="unstyled"
                      placeholder="Entity type (optional)"
                      value={rule.entityType}
                      onChange={e =>
                        useStore.getState().editGlobalRule(rule.id, {
                          entityType: e.target.value
                        })
                      }
                    />
                  </Table.Td>
                  <Table.Td>
                    <Select
                      variant="unstyled"
                      data={ruleOptions}
                      comboboxProps={{ withinPortal: false }}
                      value={rule.type}
                      onChange={type =>
                        type &&
                        handleRuleTypeChange(
                          rule.id,
                          type as AnswerTableRule["type"]
                        )
                      }
                    />
                  </Table.Td>
                  <Table.Td>
                    {rule.type === "max_length" ? (
                      <NumberInput
                        variant="unstyled"
                        min={1}
                        decimalScale={0}
                        placeholder="Max length"
                        value={rule.length ?? 1}
                        onChange={length =>
                          useStore.getState().editGlobalRule(rule.id, {
                            length: isString(length) ? 1 : length
                          })
                        }
                      />
                    ) : (
                      <TagsInput
                        variant="unstyled"
                        placeholder="Values"
                        value={rule.options ?? []}
                        onChange={options =>
                          useStore
                            .getState()
                            .editGlobalRule(rule.id, { options })
                        }
                      />
                    )}
                  </Table.Td>
                  <Table.Td>
                    <Group gap={4} wrap="nowrap">
                      <Info>{ruleInfo[rule.type]}</Info>
                      <ActionIcon
                        color="red"
                        onClick={() =>
                          useStore.getState().deleteGlobalRules([rule.id])
                        }
                      >
                        <IconTrash />
                      </ActionIcon>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        )}
        <Divider mt="md" />
        <Group mt="md">
          <Button flex={1} leftSection={<IconPlus />} onClick={handleAddRule}>
            Add rule
          </Button>
          <Button
            flex={1}
            color="red"
            variant="light"
            leftSection={<IconTrash />}
            onClick={() => useStore.getState().deleteGlobalRules()}
          >
            Clear
          </Button>
        </Group>
      </Modal>
      {!isEmpty(rules) && (
        <Paper withBorder py={4} px="xs">
          <Text>
            {rules.length} {plur("rule", rules)}
          </Text>
        </Paper>
      )}
    </Group>
  );
}

// Utils

const csvJsonSchema = z.array(
  z.object({
    rule_type: z.enum(["must_return", "may_return", "max_length", "resolve_entity"]),
    value: z.string(),
    entity_type: z.string().optional()
  })
);

function safeInt(value: string) {
  const intValue = parseInt(value);
  return isNaN(intValue) ? 1 : intValue;
}
