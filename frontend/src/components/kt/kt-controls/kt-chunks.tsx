import { useMemo } from "react";
import { Blockquote, Modal, Stack, Text } from "@mantine/core";
import { isEmpty, pick, values } from "lodash-es";
import { useStore } from "@config/store";

export function KtChunks() {
  const allChunks = useStore(store => store.getTable().chunks);
  const openedChunks = useStore(store => store.getTable().openedChunks);
  const chunks = useMemo(
    () => values(pick(allChunks, openedChunks)).flat(),
    [allChunks, openedChunks]
  );

  return (
    <Modal
      size="xl"
      title="Chunks"
      opened={!isEmpty(openedChunks)}
      onClose={() => useStore.getState().closeChunks()}
    >
      {isEmpty(chunks) ? (
        <Text>No chunks found for selected cells</Text>
      ) : (
        <Stack>
          {chunks.map((chunk, index) => (
            <Blockquote key={index}>{chunk.content}</Blockquote>
          ))}
        </Stack>
      )}
    </Modal>
  );
}
