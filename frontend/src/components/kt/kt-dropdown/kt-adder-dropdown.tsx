import { useState } from "react";
import { BoxProps } from "@mantine/core";
import { KtPromptSettings } from "../kt-prompt-settings";
import { Prompt, useStore } from "@config/store";

export function KtAdderDropdown(props: BoxProps) {
  const [input, setInput] = useState<Omit<Prompt, "id">>(defaultPrompt);

  const handleAdd = () => {
    useStore.getState().addColumn(input);
    setInput(defaultPrompt);
  };

  return (
    <KtPromptSettings
      value={input}
      onChange={setInput}
      onAdd={handleAdd}
      {...props}
    />
  );
}

// Other

const defaultPrompt: Omit<Prompt, "id"> = {
  entityType: "",
  query: "",
  type: "str",
  rules: []
};
