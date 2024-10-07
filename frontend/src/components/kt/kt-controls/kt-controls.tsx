import { BoxProps, Button, Group } from "@mantine/core";
import { IconEyeOff, IconTrash } from "@tabler/icons-react";
import { KtFilters } from "./kt-filters";
import { KtHiddenPill } from "./kt-hidden-pill";
import { KtSelection } from "./kt-selection";
import { DownloadCsvButton, ExportTriplesButton } from "./kt-download";
import { useStore } from "@config/store";

export function KtControls(props: BoxProps) {

  const clearAllData = () => {
    if (window.confirm("Are you sure you want to delete all data and start fresh?")) {
      useStore.getState().clearAllData();
    }
  };

  return (
    <Group h={30} {...props}>
      <Button
        leftSection={<IconEyeOff />}
        onClick={() => useStore.getState().toggleAllColumns(true)}
      >
        Hide all columns
      </Button>
      <Button
        leftSection={<IconTrash />}
        onClick={clearAllData}>
        Clear All Data
      </Button>
      <KtFilters />
      <KtHiddenPill />
      <KtSelection />
      <DownloadCsvButton />
      <ExportTriplesButton />
    </Group>
  );
}
