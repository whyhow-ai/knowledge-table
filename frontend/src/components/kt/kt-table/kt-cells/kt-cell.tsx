import {
  Cell,
  CellTemplate,
  Compatible,
  keyCodes,
  Uncertain,
  UncertainCompatible
} from "@silevis/reactgrid";
import {
  Checkbox,
  Loader,
  NumberInput,
  TagsInput,
  Textarea
} from "@mantine/core";
import { isNil } from "lodash-es";
import { formatCell, isKtCell, EditorWrapper } from "./kt-cell.utils";
import {
  AnswerTableColumn,
  AnswerTableRow,
  useStore,
  CellValue,
  getCellKey,
  castToType,
  castToString,
  castToInt,
  castToBool,
  castToStrArray,
  castToIntArray
} from "@config/store";

export interface KtCell extends Cell {
  type: "kt-cell";
  column: AnswerTableColumn;
  row: AnswerTableRow;
  cell: CellValue;
}

export class KtCellTemplate implements CellTemplate<KtCell> {
  getCompatibleCell(cell: Uncertain<KtCell>): Compatible<KtCell> {
    if (!isKtCell(cell)) {
      throw new Error("Invalid cell type");
    }
    return {
      ...cell,
      type: "kt-cell",
      column: cell.column,
      row: cell.row,
      cell: cell.cell,
      text: castToString(cell.cell) ?? "",
      value: NaN
    };
  }

  update(
    cell: Compatible<KtCell>,
    cellToMerge: UncertainCompatible<KtCell>
  ): Compatible<KtCell> {
    const value =
      isKtCell(cellToMerge) &&
      (cellToMerge.column.type === cell.column.type || isNil(cellToMerge.cell))
        ? cellToMerge.cell
        : castToType(cellToMerge.text, cell.column.type);
    return this.getCompatibleCell({ ...cell, cell: value });
  }

  handleKeyDown(
    cell: Compatible<KtCell>,
    keyCode: number
  ): { cell: Compatible<KtCell>; enableEditMode: boolean } {
    const key = getCellKey(cell.row, cell.column);
    const loading = useStore.getState().getTable().loadingCells[key];
    return {
      cell,
      enableEditMode:
        !loading && (keyCode === keyCodes.POINTER || keyCode === keyCodes.ENTER)
    };
  }

  render(
    cell: Compatible<KtCell>,
    isInEditMode: boolean,
    onCellChanged: (cell: Compatible<KtCell>, commit: boolean) => void
  ) {
    const handleChange = (cellValue: CellValue, commit = false) => {
      onCellChanged(
        this.getCompatibleCell({ ...cell, cell: cellValue }),
        commit
      );
    };
    return (
      <Content cell={cell} editMode={isInEditMode} onChange={handleChange} />
    );
  }
}

// Content

interface ContentProps {
  cell: KtCell;
  editMode: boolean;
  onChange: (value: CellValue, commit?: boolean) => void;
}

function Content({
  cell: { column, row, cell },
  editMode,
  onChange
}: ContentProps) {
  const key = getCellKey(row, column);
  const loading = useStore(store => store.getTable().loadingCells[key]);

  if (loading) {
    return <Loader size="xs" />;
  }
  if (!editMode) {
    return formatCell(cell);
  }

  return (
    <EditorWrapper defaultValue={cell} onChange={onChange}>
      {(inputProps, handleChange) => {
        switch (column.type) {
          case "str":
            return (
              <Textarea
                {...inputProps}
                autosize
                maxRows={6}
                variant="unstyled"
                defaultValue={castToString(cell) ?? undefined}
                onChange={e => handleChange(e.target.value)}
              />
            );

          case "int":
            return (
              <NumberInput
                {...inputProps}
                variant="unstyled"
                decimalScale={0}
                defaultValue={castToInt(cell) ?? undefined}
                onChange={value => handleChange(castToInt(value))}
              />
            );

          case "bool":
            return (
              <Checkbox
                {...inputProps}
                m="xs"
                defaultChecked={castToBool(cell) ?? undefined}
                onChange={e => handleChange(e.target.checked)}
              />
            );

          case "str_array":
            return (
              <TagsInput
                {...inputProps}
                variant="unstyled"
                defaultValue={castToStrArray(cell) ?? undefined}
                onChange={value => handleChange(value)}
              />
            );

          case "int_array":
            return (
              <TagsInput
                {...inputProps}
                variant="unstyled"
                defaultValue={castToIntArray(cell)?.map(String) ?? undefined}
                onChange={value => handleChange(castToIntArray(value))}
                onKeyDown={e =>
                  !e.ctrlKey && /^[a-z]$/i.test(e.key) && e.preventDefault()
                }
              />
            );
          default:
            return null;
        }
      }}
    </EditorWrapper>
  );
}
