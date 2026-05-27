"use client";

import * as React from "react";
import { motion, type HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

type ButtonProps = Omit<HTMLMotionProps<"button">, "children"> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg" | "icon";
  icon?: React.ReactNode;
  children?: React.ReactNode;
};

const variants = {
  primary: "bg-studio-cyan text-gm-on-primary hover:bg-studio-cyan/90",
  secondary: "border border-studio-line text-studio-text hover:border-studio-cyan/60 hover:bg-studio-panel2/40",
  ghost: "bg-transparent text-studio-muted hover:bg-studio-panel2/60 hover:text-studio-text",
  danger: "bg-studio-red text-white hover:bg-studio-red/90"
};

const sizes = {
  sm: "h-8 px-4 text-sm",
  md: "h-9 px-5 text-sm",
  lg: "h-11 px-7 text-base",
  icon: "h-10 w-10 p-0"
};

export function Button({ className, variant = "primary", size = "md", icon, children, ...props }: ButtonProps) {
  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      className={cn(
        "focus-ring inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-colors duration-150 disabled:pointer-events-none disabled:opacity-45",
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {icon}
      {children}
    </motion.button>
  );
}
