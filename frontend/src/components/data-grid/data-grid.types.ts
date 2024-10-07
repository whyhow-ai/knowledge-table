import { ReactNode } from "react";

export type DataGridCell = {
  key: string;
  groupKey?: string;
  width?: number;
  content: ReactNode;
  dropdown?: DataGridDropdown;
  onClick?: () => void;
};

export type DataGridCellWithoutKey = Omit<DataGridCell, "key">;

export type DataGridDropdown = {
  scrollable?: boolean;
  content: ReactNode;
};

export type DataGridDrag = {
  start: string;
  end: string;
  ctrl: boolean;
  initialSelection: string[];
};
