import { ReactNode } from "react";
import {
  IconAlignJustified,
  IconCheckbox,
  IconHash,
  TablerIcon
} from "@tabler/icons-react";
import { Prompt, PromptRule } from "@config/store";

export const typeOptions: {
  value: Prompt["type"];
  label: ReactNode;
  icon: TablerIcon;
}[] = [
  { value: "str", label: "Text", icon: IconAlignJustified },
  { value: "str_array", label: "List of text", icon: IconAlignJustified },
  { value: "int", label: "Number", icon: IconHash },
  { value: "int_array", label: "List of numbers", icon: IconHash },
  { value: "bool", label: "True / False", icon: IconCheckbox }
];

export const ruleOptions: {
  value: PromptRule["type"];
  label: string;
}[] = [
  { value: "must_return", label: "Must return" },
  { value: "may_return", label: "May return" },
  { value: "max_length", label: "Allowed # of responses" }
];

export const defaultRules: Record<PromptRule["type"], PromptRule> = {
  must_return: { type: "must_return", options: [] },
  may_return: { type: "may_return", options: [] },
  max_length: { type: "max_length", length: 1 }
};

export const ruleInfo: Record<PromptRule["type"], string> = {
  must_return: "The column must return the specified values",
  may_return: "The column may return the specified values",
  max_length: "The column must return at most N values"
};
