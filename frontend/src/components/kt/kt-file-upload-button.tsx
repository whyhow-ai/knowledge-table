import { useRef, forwardRef, useEffect } from "react";
import { BoxProps, Button, FileButton, Loader } from "@mantine/core";
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
        {uploadingFiles ? (
          <Loader size="xs" />
        ) : (
          <IconPlus size={16} opacity={0.7} />
        )}
        <FileButton
          resetRef={resetRef}
          multiple
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
