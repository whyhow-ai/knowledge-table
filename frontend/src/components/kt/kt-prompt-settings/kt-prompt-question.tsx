import { ColorSwatch, Group, InputWrapperProps } from "@mantine/core";
import { useStore } from "@config/store";
import { Mention } from "@components";
import { entityColor } from "@utils/functions";

interface Props extends Omit<InputWrapperProps, "onChange"> {
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
}

export function KtPromptQuestion({
  placeholder,
  value,
  onChange,
  ...props
}: Props) {
  const columns = useStore(store => store.columns);
  return (
    <Mention
      required
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      options={[
        {
          trigger: "@",
          data: columns.map(column => ({
            id: column.id,
            display: column.prompt.entityType
          })),
          color: item => entityColor(item.display ?? "").fill,
          render: item => {
            const color = entityColor(item.display ?? "").fill;
            return (
              <Group>
                <ColorSwatch size={12} color={color} />
                <span>{item.display}</span>
              </Group>
            );
          }
        }
      ]}
      {...props}
    />
  );
}
