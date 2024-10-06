import { ReactNode } from "react";
import { pack } from "@utils/functions";
import { Pack } from "@utils/types";

export interface WrapProps {
  children: ReactNode;
  with?: Pack<(children: ReactNode) => ReactNode>;
}

export function Wrap({ children, with: factories }: WrapProps) {
  return (
    <>
      {pack(factories).reduceRight(
        (children, factory) => factory(children),
        children
      )}
    </>
  );
}
