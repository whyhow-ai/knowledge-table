import { ReactNode } from "react";
import {
  IconAccessPoint,
  IconAccessPointOff,
  IconAlignJustified,
  IconCheckbox,
  IconHash,
  TablerIcon
} from "@tabler/icons-react";
import { AnswerTableColumn } from "@config/store";

export const typeOptions: {
  value: AnswerTableColumn["type"];
  label: ReactNode;
  icon: TablerIcon;
}[] = [
  { value: "str", label: "Text", icon: IconAlignJustified },
  { value: "str_array", label: "List of text", icon: IconAlignJustified },
  { value: "int", label: "Number", icon: IconHash },
  { value: "int_array", label: "List of numbers", icon: IconHash },
  { value: "bool", label: "True / False", icon: IconCheckbox }
];

export const generateOptions: {
  value: boolean;
  label: ReactNode;
  icon: TablerIcon;
}[] = [
  { value: true, label: "Enabled", icon: IconAccessPoint },
  { value: false, label: "Disabled", icon: IconAccessPointOff }
];
