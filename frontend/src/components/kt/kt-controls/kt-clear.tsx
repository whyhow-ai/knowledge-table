import { useState } from "react";
import { Button, Group, Radio, Stack } from "@mantine/core";
import { modals } from "@mantine/modals";
import { IconTrash } from "@tabler/icons-react";
import { useStore } from "@config/store";

export function KtClear() {
  return (
    <Button
      leftSection={<IconTrash />}
      onClick={() =>
        modals.open({
          size: "xs",
          title: "Clear",
          children: <ConfirmClearModalContent />
        })
      }
    >
      Clear
    </Button>
  );
}

function ConfirmClearModalContent() {
  const [mode, setMode] = useState("this");
  const handleConfirm = () => {
    useStore.getState().clear(mode === "all");
    modals.closeAll();
  };

  return (
    <>
      <Radio.Group value={mode} onChange={setMode}>
        <Stack gap="xs">
          <Radio value="this" label="Clear this table only" />
          <Radio value="all" label="Clear all tables and start fresh" />
        </Stack>
      </Radio.Group>
      <Group mt="md" justify="end">
        <Button variant="default" onClick={() => modals.closeAll()}>
          Cancel
        </Button>
        <Button onClick={handleConfirm}>Confirm</Button>
      </Group>
    </>
  );
}
