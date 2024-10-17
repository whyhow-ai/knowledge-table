import { useRef, forwardRef, useEffect } from "react";
import {
  BoxProps,
  Button,
  FileButton,
  Group,
  Loader,
  Text
} from "@mantine/core";
import { IconPlus } from "@tabler/icons-react";
import { useStore } from "@config/store";

export const KtFileUploadButton = forwardRef<HTMLButtonElement, BoxProps>(
  (props, ref) => {
    const uploadingFiles = useStore(store => store.uploadingFiles);
    const resetRef = useRef<() => void>(null);

    useEffect(() => {
      !uploadingFiles && resetRef.current?.();
    }, [uploadingFiles]);

    return (
      <>
        <Group h="100%">
          {uploadingFiles ? (
            <Loader size="xs" />
          ) : (
            <IconPlus size={18} opacity={0.7} />
          )}
          <div>
            <Text fw={500}>Add documents</Text>
            <Text size="xs" c="dimmed">
              Formats: pdf, txt
            </Text>
          </div>
        </Group>
        <FileButton
          resetRef={resetRef}
          multiple
          accept="application/pdf,text/plain"
          onChange={useStore.getState().addRows}
        >
          {fileProps => (
            <Button ref={ref} {...props} {...fileProps}>
              Add Document
            </Button>
          )}
        </FileButton>
      </>
    );
  }
);
