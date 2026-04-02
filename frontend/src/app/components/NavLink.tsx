"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/app/lib/utils";

interface NavLinkProps {
  href: string;
  className?: string;
  activeClassName?: string;
  pendingClassName?: string; // ignored in Next (no pending state)
  children: React.ReactNode;
}

export function NavLink({
  href,
  className,
  activeClassName,
  pendingClassName, // not used in Next but kept for compatibility
  children,
  ...props
}: NavLinkProps) {
  const pathname = usePathname();

  const isActive = pathname === href;

  return (
    <Link
      href={href}
      className={cn(className, isActive && activeClassName)}
      {...props}
    >
      {children}
    </Link>
  );
}

