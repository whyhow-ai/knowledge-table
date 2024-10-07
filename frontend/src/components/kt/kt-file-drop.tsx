import { useEffect, useState } from "react";
import { Center, Group, Overlay, Text } from "@mantine/core";
import { IconFileUpload } from "@tabler/icons-react";
import { useStore } from "@config/store";

export function KTFileDrop() {
  const [draggingOver, setDraggingOver] = useState(false);

  useEffect(() => {
    const root = document.getElementById("root");
    if (!root) return;

    const handleDragEnter = () => {
      setDraggingOver(true);
    };
    const handleDragLeave = (e: DragEvent) => {
      if (!root.contains(e.relatedTarget as any)) {
        setDraggingOver(false);
      }
    };
    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
    };
    const handleDrop = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDraggingOver(false);
      const files = e.dataTransfer?.files;
      if (files) {
        useStore.getState().addRows([...files]);
      }
    };

    root.addEventListener("dragenter", handleDragEnter);
    root.addEventListener("dragleave", handleDragLeave);
    root.addEventListener("dragover", handleDragOver);
    root.addEventListener("drop", handleDrop);
    return () => {
      root.removeEventListener("dragenter", handleDragEnter);
      root.removeEventListener("dragleave", handleDragLeave);
      root.removeEventListener("dragover", handleDragOver);
      root.removeEventListener("drop", handleDrop);
    };
  }, []);

  return (
    draggingOver && (
      <Overlay style={{ pointerEvents: "none" }}>
        <Center h="100%">
          <Group>
            <IconFileUpload size={60} color="white" />
            <Text c="white" size="md" fw={500}>
              Drop files
            </Text>
          </Group>
        </Center>
      </Overlay>
    )
  );
}
