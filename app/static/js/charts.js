/* Graphiques RentImmo — palette catégorielle validée (ordre fixe, jamais recyclée).
   Contraintes dataviz : lignes 2px, barres fines à coins arrondis 4px, grille
   discrète, légende dès 2 séries, tooltips systématiques, un seul axe Y. */

const RENTIMMO = {
  palette: ["#005291", "#00bcaa", "#e08a00", "#8a5cf5"],
  grid: "#e9ecef",
  ink: "#495057",

  fmt(valeur) {
    return new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 0 }).format(valeur);
  },

  baseOptions(devise) {
    const fmt = this.fmt;
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        tooltip: {
          callbacks: {
            label(ctx) {
              const v = ctx.parsed.y ?? ctx.parsed;
              return `${ctx.dataset.label || ctx.label} : ${fmt(v)} ${devise}`;
            },
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#6c757d" } },
        y: {
          grid: { color: "#e9ecef" },
          border: { display: false },
          ticks: { color: "#6c757d", callback: (v) => fmt(v) },
        },
      },
    };
  },
};
