import { ReactNode } from "react";
import {
  BoxProps,
  Blockquote,
  Stack,
  Badge,
  Text,
  Textarea,
  NumberInput,
  SegmentedControl,
  TagsInput
} from "@mantine/core";
import { castArray, debounce, isArray, isBoolean, isNumber } from "lodash-es";
import { Answer, AnswerTableCell, useStore } from "@config/store";
import { Highlight } from "@components";

interface Props extends BoxProps {
  cell: AnswerTableCell;
}

export function KtCellDropdown({ cell, ...props }: Props) {
  return (
    <>
      <CellEditor cell={cell} />
      <Text fw={500} mt="sm">
        Chunks
      </Text>
      <Stack mt="xs" {...props}>
        {cell.answer.chunks.map((chunk, i) => (
          <Blockquote
            key={i}
            px="md"
            py="xs"
            cite={`Page ${chunk.page}`}
            styles={{ cite: { marginTop: 0 } }}
          >
            <Highlight
              key={i}
              highlights={[
                {
                  color: "blue",
                  words: castArray(cell.answer.answer).map(String)
                }
              ]}
            >
              {chunk.content}
            </Highlight>
          </Blockquote>
        ))}
      </Stack>
    </>
  );
}

function CellEditor({ cell }: Props) {
  const { answer } = cell;
  const handleChange = (
    answer: string | number | boolean | string[] | number[]
  ) => debouncedEditCell(cell, { answer });

  switch (answer.type) {
    case "str":
      return (
        <Textarea
          placeholder="Value"
          defaultValue={String(answer.answer)}
          onChange={e => handleChange(e.target.value)}
        />
      );
    case "int":
      return (
        <NumberInput
          placeholder="Value"
          defaultValue={Number(answer.answer)}
          onChange={v => isNumber(v) && handleChange(v)}
        />
      );
    case "bool":
      return (
        <SegmentedControl
          data={["true", "false"]}
          defaultValue={String(Boolean(answer.answer))}
          onChange={v => handleChange(v === "true")}
        />
      );
    case "str_array":
      return (
        <TagsInput
          placeholder="Value"
          defaultValue={castArray(answer.answer)
            .filter(value => value !== null)
            .map(String)}
          onChange={values => handleChange(values)}
        />
      );
    case "int_array":
      return (
        <TagsInput
          placeholder="Value"
          defaultValue={castArray(answer.answer)
            .filter(value => value !== null)
            .map(String)}
          onChange={values => handleChange(values.map(Number))}
        />
      );
  }
}

// Utils

export function formatAnswer({ answer }: Answer): ReactNode {
  if (answer === null) {
    return <Text c="dimmed">Not found</Text>;
  } else if (isBoolean(answer)) {
    return <Badge>{String(answer)}</Badge>;
  } else {
    return (
      <Text lineClamp={3}>{isArray(answer) ? answer.join(", ") : answer}</Text>
    );
  }
}

const debouncedEditCell = debounce(useStore.getState().editCell, 500);
