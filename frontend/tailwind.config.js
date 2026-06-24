export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#2a160d",
        night: "#1f1712",
        panel: "#d8b77d",
        paper: "#f0d8a4",
        brass: "#c99045",
        crimson: "#7d3328",
        wax: "#4a1d16",
      },
      fontFamily: {
        display: ["Cinzel Decorative", "Cinzel", "Georgia", "serif"],
        body: ["Cinzel", "Georgia", "serif"],
      },
      boxShadow: {
        dossier: "0 24px 70px rgba(17, 19, 24, 0.24)",
        card: "0 14px 35px rgba(17, 19, 24, 0.13)",
      },
    },
  },
  plugins: [],
};
