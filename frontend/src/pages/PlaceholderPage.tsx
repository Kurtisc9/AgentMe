import type { ReactNode } from "react";

export function PlaceholderPage({
  title,
  description,
  icon,
  children,
}: {
  title: string;
  description: string;
  icon: ReactNode;
  children?: ReactNode;
}) {
  return (
    <section className="panel page-panel">
      <div className="panel-heading">
        {icon}
        <h2>{title}</h2>
      </div>
      <p className="page-description">{description}</p>
      {children}
    </section>
  );
}
