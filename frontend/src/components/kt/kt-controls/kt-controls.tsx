import { BoxProps, Button, Group, Text } from "@mantine/core";
import { modals } from "@mantine/modals";
import { IconEyeOff, IconTrash } from "@tabler/icons-react";
import { KtFilters } from "./kt-filters";
import { KtHiddenPill } from "./kt-hidden-pill";
import { KtSelection } from "./kt-selection";
import { KtDownload } from "./kt-download";
import { useStore } from "@config/store";

export function KtControls(props: BoxProps) {
  const handleClear = () => {
    modals.openConfirmModal({
      title: "Clear all data",
      children: (
        <Text>Are you sure you want to delete all data and start fresh?</Text>
      ),
      labels: { confirm: "Confirm", cancel: "Cancel" },
      onConfirm: useStore.getState().clear
    });
  };

  return (
    <Group h={30} {...props}>
      <Button
        leftSection={<IconEyeOff />}
        onClick={() => useStore.getState().toggleAllColumns(true)}
      >
        Hide all columns
      </Button>
      <Button leftSection={<IconTrash />} onClick={handleClear}>
        Clear all data
      </Button>
      <KtFilters />
      <KtHiddenPill />
      <KtSelection />
      <KtDownload.Csv />
      <KtDownload.Triples />
    </Group>
  );
}
