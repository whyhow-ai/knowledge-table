import { Text, BoxProps, Paper, Group, Anchor } from "@mantine/core";
import { isEmpty } from "lodash-es";
import { useStore } from "@config/store";
import { plur } from "@utils/functions";

export function KtSelection(props: BoxProps) {
  const selection = useStore(store => store.selection);
  const handleRerun = () => {
    useStore.getState().rerunCells(
      selection.map(id => {
        const [rowId, columnId] = id.split("-");
        return { rowId, columnId };
      })
    );
  };

  return (
    !isEmpty(selection) && (
      <Paper withBorder py={4} px="xs" {...props}>
        <Group>
          <Text>
            {selection.length} {plur("cell", selection)} selected
          </Text>
          <Anchor onClick={handleRerun}>Rerun</Anchor>
        </Group>
      </Paper>
    )
  );
}
