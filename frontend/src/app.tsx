import { QueryClientProvider } from "@tanstack/react-query";
import { ActionIcon, Divider, Group, MantineProvider } from "@mantine/core";
import { IconMoon, IconSun } from "@tabler/icons-react";
import "@mantine/core/styles.css";
import { queryClient } from "@config/query";
import { useTheme } from "@config/theme";
import { useStore } from "@config/store";
import { KtTable, KTFileDrop, KtSwitch, KtControls } from "@components";
import "./app.css";

export function App() {
  const theme = useTheme();
  const colorScheme = useStore(store => store.colorScheme);
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider theme={theme} forceColorScheme={colorScheme}>
        <Group p="md" justify="space-between">
          <KtSwitch />
          <ActionIcon onClick={useStore.getState().toggleColorScheme}>
            {colorScheme === "light" ? <IconSun /> : <IconMoon />}
          </ActionIcon>
        </Group>
        <Divider />
        <KtControls mt="md" ml="md" />
        <KtTable mt="md" />
        <KTFileDrop />
      </MantineProvider>
    </QueryClientProvider>
  );
}
