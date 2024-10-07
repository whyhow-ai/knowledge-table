import { useMemo } from "react";
import {
  Box,
  BoxProps,
  Button,
  Divider,
  Group,
  Textarea,
  TextInput,
  Text,
  Menu,
  ActionIcon,
  Select,
  NumberInput,
  TagsInput,
  Tooltip
} from "@mantine/core";
import {
  IconArrowAutofitHeight,
  IconCirclePlus,
  IconEyeOff,
  IconPlus,
  IconReload,
  IconTrash
} from "@tabler/icons-react";
import { cloneDeep, isEmpty, isString } from "lodash-es";
import {
  defaultRules,
  ruleInfo,
  ruleOptions,
  typeOptions
} from "./kt-prompt-settings.utils";
import { Prompt, PromptRule, isArrayType } from "@config/store";
import { Empty, Info, MenuButton } from "@components";
import { plur } from "@utils/functions";

interface Props extends BoxProps {
  value: Omit<Prompt, "id">;
  onAdd?: () => void;
  onChange?: (value: Omit<Prompt, "id">) => void;
  onRerun?: () => void;
  onUnwind?: () => void;
  onHide?: () => void;
  onDelete?: () => void;
}

export function KtPromptSettings({
  value,
  onAdd,
  onChange,
  onRerun,
  onUnwind,
  onHide,
  onDelete,
  ...props
}: Props) {
  const readonly = !onChange;
  const submitDisabled = !value.entityType.trim() || !value.query.trim();
  const typeOption = useMemo(
    () => typeOptions.find(option => option.value === value.type),
    [value.type]
  );
  const TypeIcon = typeOption?.icon;

  const handleChange = (changes: Partial<Prompt>) => {
    onChange?.({ ...value, ...changes });
  };

  const handleAddRule = () => {
    handleChange({
      rules: [...value.rules, { type: "must_return", options: [] }]
    });
  };

  const handleRuleTypeChange = (rule: PromptRule, type: PromptRule["type"]) => {
    handleChange({
      rules: value.rules.map(r =>
        r === rule ? cloneDeep(defaultRules[type]) : r
      )
    });
  };

  const handleRuleLengthChange = (rule: PromptRule, length: number) => {
    handleChange({
      rules: value.rules.map(r => (r === rule ? { ...r, length } : r))
    });
  };

  const handleRuleOptionsChange = (rule: PromptRule, options: string[]) => {
    handleChange({
      rules: value.rules.map(r => (r === rule ? { ...r, options } : r))
    });
  };

  const handleDeleteRule = (rule: PromptRule) => {
    handleChange({
      rules: value.rules.filter(r => r !== rule)
    });
  };

  const rulesMenu = (
    <Box w={430}>
      {isEmpty(value.rules) ? (
        <Empty message="No rules are applied" />
      ) : (
        value.rules.map((rule, index) => (
          <Group key={index} mb="xs" gap="xs" wrap="nowrap">
            <Select
              variant="unstyled"
              data={ruleOptions}
              comboboxProps={{ withinPortal: false }}
              value={rule.type}
              onChange={type =>
                type && handleRuleTypeChange(rule, type as PromptRule["type"])
              }
            />
            {rule.type === "max_length" ? (
              <NumberInput
                w={150}
                min={1}
                decimalScale={0}
                placeholder="Max length"
                value={rule.length}
                onChange={length =>
                  handleRuleLengthChange(rule, isString(length) ? 1 : length)
                }
              />
            ) : (
              <TagsInput
                w={210}
                placeholder="Values"
                value={rule.options}
                onChange={options => handleRuleOptionsChange(rule, options)}
              />
            )}
            <Info>{ruleInfo[rule.type]}</Info>
            <ActionIcon color="red" onClick={() => handleDeleteRule(rule)}>
              <IconTrash />
            </ActionIcon>
          </Group>
        ))
      )}
      <Divider mt="xs" />
      <Group mt="xs">
        <Button flex={1} leftSection={<IconPlus />} onClick={handleAddRule}>
          Add rule
        </Button>
        <Button
          flex={1}
          color="red"
          variant="light"
          leftSection={<IconTrash />}
          onClick={() => handleChange({ rules: [] })}
        >
          Clear
        </Button>
      </Group>
    </Box>
  );

  return (
    <Box {...props}>
      <Group gap="xs" wrap="nowrap" justify="space-between">
        <TextInput
          autoFocus
          fw={500}
          size="md"
          variant="unstyled"
          disabled={readonly}
          placeholder="Entity type"
          value={value.entityType}
          onChange={e => handleChange({ entityType: e.target.value })}
        />
        <Group gap="xs" wrap="nowrap">
          {onRerun && (
            <Tooltip label="Rerun column">
              <ActionIcon onClick={onRerun}>
                <IconReload />
              </ActionIcon>
            </Tooltip>
          )}
          {onUnwind && isArrayType(value.type) && (
            <Tooltip label="Split cells into rows">
              <ActionIcon onClick={onUnwind}>
                <IconArrowAutofitHeight />
              </ActionIcon>
            </Tooltip>
          )}
          {onHide && (
            <Tooltip label="Hide column">
              <ActionIcon onClick={onHide}>
                <IconEyeOff />
              </ActionIcon>
            </Tooltip>
          )}
          {onDelete && (
            <Tooltip label="Delete column">
              <ActionIcon color="red" onClick={onDelete}>
                <IconTrash />
              </ActionIcon>
            </Tooltip>
          )}
        </Group>
      </Group>
      <Divider mt="xs" mx="calc(var(--mantine-spacing-sm) * -1)" />
      <MenuButton
        mt="xs"
        label="Rules"
        disabled={readonly}
        dropdownProps={{ p: "sm" }}
        menu={rulesMenu}
        rightSection={
          <Text c="dimmed">
            {value.rules.length} {plur("rule", value.rules)}
          </Text>
        }
      />
      <MenuButton
        mt="xs"
        label="Type"
        disabled={readonly}
        rightSection={
          <Group c="dimmed">
            {TypeIcon && <TypeIcon size={16} />}
            <Text>{typeOption?.label}</Text>
          </Group>
        }
        menu={typeOptions.map(({ value: type, label, icon: Icon }) => (
          <Menu.Item
            key={type}
            onClick={() => handleChange({ type })}
            leftSection={<Icon />}
          >
            {label}
          </Menu.Item>
        ))}
      />
      <Textarea
        mt="xs"
        autosize
        required
        minRows={3}
        label="Question"
        placeholder="Question"
        disabled={readonly}
        value={value.query}
        onChange={e => handleChange({ query: e.target.value })}
      />
      {onAdd && (
        <Button
          mt="xs"
          fullWidth
          color="blue"
          variant="light"
          leftSection={<IconCirclePlus />}
          onClick={onAdd}
          disabled={submitDisabled}
        >
          Submit
        </Button>
      )}
    </Box>
  );
}
