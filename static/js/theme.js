document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("theme-toggle");
    if (!toggle) return;

    const root = document.documentElement;
    const icon = toggle.querySelector("i");
    const label = toggle.querySelector(".nav_title");

    const lightLabel = toggle.dataset.lightLabel;
    const darkLabel = toggle.dataset.darkLabel;

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
        root.setAttribute("data-theme", savedTheme);
    }

    function updateUI(theme) {
        if (theme === "dark") {
            icon.className = "nav_icon fa-solid fa-sun";
            label.textContent = lightLabel;
        } else {
            icon.className = "nav_icon fa-solid fa-moon";
            label.textContent = darkLabel;
        }
    }

    const currentTheme = root.getAttribute("data-theme") || "light";
    updateUI(currentTheme);

    toggle.addEventListener("click", (e) => {
        e.preventDefault();

        const current = root.getAttribute("data-theme");
        const next = current === "dark" ? "light" : "dark";

        root.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);

        updateUI(next);
    });
});