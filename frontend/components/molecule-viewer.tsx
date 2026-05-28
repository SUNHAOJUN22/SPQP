"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Atom, Rotate3D } from "lucide-react";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import type { StudioMolecule } from "@/types/studio";
import { cn } from "@/lib/utils";

declare global {
  interface Window {
    $3Dmol?: {
      createViewer: (element: HTMLElement, options: Record<string, unknown>) => {
        addModel: (data: string, format: string) => void;
        setStyle: (selector: Record<string, unknown>, style: Record<string, unknown>) => void;
        zoomTo: () => void;
        render: () => void;
        clear: () => void;
      };
    };
  }
}

const atomColors: Record<string, string> = {
  C: "bg-studio-panel3",
  Si: "bg-studio-violet",
  O: "bg-studio-red",
  Cl: "bg-studio-green",
  Al: "bg-studio-orange",
  Ti: "bg-studio-blue"
};

function atomsFromSmiles(smiles: string) {
  const tokens = smiles.match(/Si|Cl|Al|Ti|[A-Z]/g) ?? ["C", "C", "Si"];
  return tokens.slice(0, 14);
}

export function MoleculeViewer({ molecule, highlight = "Si–O / Si–C 高亮" }: { molecule: StudioMolecule; highlight?: string }) {
  const ref = useRef<HTMLDivElement | null>(null);
  const [useFallback, setUseFallback] = useState(true);
  const atoms = useMemo(() => atomsFromSmiles(molecule.smiles), [molecule.smiles]);

  useEffect(() => {
    const element = ref.current;
    if (!element || !window.$3Dmol) {
      return;
    }
    let frame = 0;
    try {
      const viewer = window.$3Dmol.createViewer(element, { backgroundColor: "transparent" });
      viewer.clear();
      viewer.addModel("", "xyz");
      viewer.setStyle({}, { sphere: { radius: 0.45 }, stick: { radius: 0.18 } });
      viewer.zoomTo();
      viewer.render();
      frame = window.requestAnimationFrame(() => setUseFallback(false));
    } catch {
      frame = window.requestAnimationFrame(() => setUseFallback(true));
    }
    return () => {
      if (frame) {
        window.cancelAnimationFrame(frame);
      }
    };
  }, [molecule.key]);

  return (
    <div className="smooth-layer relative min-h-[360px] overflow-hidden rounded-expressive border border-studio-line bg-studio-panel molecule-grid">
      <div ref={ref} className={cn("absolute inset-0", useFallback && "hidden")} />
      {useFallback && (
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="smooth-layer relative h-72 w-72"
            animate={{ rotateY: [0, 12, -8, 0], rotateX: [0, -4, 7, 0] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          >
            <div className="absolute left-1/2 top-1/2 h-px w-56 -translate-x-1/2 bg-studio-line" />
            <div className="absolute left-[20%] top-[34%] h-px w-44 rotate-45 bg-studio-line" />
            <div className="absolute left-[30%] top-[62%] h-px w-40 -rotate-[35deg] bg-studio-line" />
            {atoms.map((atom, index) => {
              const angle = (index / atoms.length) * Math.PI * 2;
              const radius = atom === "Si" ? 12 : 106 - (index % 3) * 14;
              const x = Math.cos(angle) * radius + 136;
              const y = Math.sin(angle) * radius + 136;
              return (
                <motion.div
                  key={`${atom}-${index}`}
                  className={cn(
                    "smooth-layer absolute grid h-11 w-11 place-items-center rounded-full border border-white/20 text-xs font-medium text-studio-text shadow-elevation-2",
                    atomColors[atom] ?? "bg-studio-panel3",
                    atom === "Si" && "h-14 w-14 text-white",
                    atom === "O" && "text-white"
                  )}
                  style={{ left: x, top: y }}
                  animate={{ scale: atom === "Si" || atom === "O" ? [1, 1.08, 1] : [1, 1.03, 1] }}
                  transition={{ duration: 2.4 + index * 0.12, repeat: Infinity }}
                >
                  {atom}
                </motion.div>
              );
            })}
            {molecule.descriptors.oCount > 0 && (
              <div className="absolute left-[46%] top-[36%] h-28 w-28 rounded-full bg-studio-red/20 blur-2xl" />
            )}
          </motion.div>
        </div>
      )}
      <div className="absolute left-4 top-4 flex items-center gap-2">
        <StatusBadge tone="blue">{highlight}</StatusBadge>
        <StatusBadge tone="gray">{molecule.source}</StatusBadge>
      </div>
      <div className="absolute bottom-4 left-4 right-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 text-sm font-medium text-studio-text">
            <Atom className="h-4 w-4 text-studio-cyan" />
            {molecule.name}
          </div>
          <p className="mt-1 font-mono text-xs text-studio-muted">{molecule.smiles}</p>
        </div>
        <Button variant="secondary" size="sm" icon={<Rotate3D className="h-4 w-4" />}>
          定位活性中心
        </Button>
      </div>
    </div>
  );
}
