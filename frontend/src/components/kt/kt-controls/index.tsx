import { BoxProps, Button, Group, Text, Loader } from "@mantine/core";
import { IconEyeOff } from "@tabler/icons-react";
import { KtHiddenPill } from "./kt-hidden-pill";
import { KtClear } from "./kt-clear";
import { KtFilters } from "./kt-filters";
import { KTGlobalRules } from "./kt-global-rules";
import { KtDownload } from "./kt-download";
import { KtChunks } from "./kt-chunks";
import { useStore } from "@config/store";

export function KtControls(props: BoxProps) {
  const uploadingFiles = useStore(store => store.getTable().uploadingFiles);

  return (
    <Group gap="xs" {...props}>
      <Button
        leftSection={<IconEyeOff />}
        onClick={() => useStore.getState().toggleAllColumns(true)}
      >
        Hide all columns
      </Button>
      <KtHiddenPill />
      <KtClear />
      <KtFilters />
      <KTGlobalRules />
      <KtDownload.Csv />
      <KtDownload.Triples />
      <KtChunks />
      {uploadingFiles && (
        <Group>
          <Loader size="xs" />
          <Text>Uploading files...</Text>
        </Group>
      )}
    </Group>
  );
}
