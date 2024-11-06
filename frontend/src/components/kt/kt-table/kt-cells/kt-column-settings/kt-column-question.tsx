import { ColorSwatch, Group, InputWrapperProps } from "@mantine/core";
import { useStore } from "@config/store";
import { Mention } from "@components";
import { entityColor } from "@utils/functions";

interface Props extends Omit<InputWrapperProps, "onChange"> {
  placeholder?: string;
  disabled?: boolean;
  value?: string;
  defaultValue?: string;
  onChange: (value: string) => void;
}

export function KtColumnQuestion({
  placeholder,
  disabled,
  value,
  defaultValue,
  onChange,
  ...props
}: Props) {
  const columns = useStore(store => store.getTable().columns);
  return (
    <Mention
      required
      placeholder={placeholder}
      disabled={disabled}
      value={value}
      defaultValue={defaultValue}
      onChange={onChange}
      options={[
        {
          trigger: "@",
          data: columns
            .filter(column => column.entityType.trim())
            .map(column => ({
              id: column.id,
              display: column.entityType
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
