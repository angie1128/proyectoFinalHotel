// Automatic theme switching based on system preference
document.addEventListener("DOMContentLoaded", () => {
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")

  // Function to apply theme
  const applyTheme = (isDark) => {
    // No need to set data-theme since CSS handles it with media query
    // But if you want to force or override, you could add logic here
    console.log("Theme applied:", isDark ? "dark" : "light")
  }

  // Apply initial theme
  applyTheme(mediaQuery.matches)

  // Listen for changes
  mediaQuery.addEventListener("change", (e) => {
    applyTheme(e.matches)
  })
})

// Auto-dismiss alerts after 5 seconds
document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".alert")
  const bootstrap = window.bootstrap // Declare the bootstrap variable
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert)
      bsAlert.close()
    }, 5000)
  })
})

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute("href"))
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  })
})

// Form validation enhancement
document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll("form")
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!form.checkValidity()) {
        e.preventDefault()
        e.stopPropagation()
      }
      form.classList.add("was-validated")
    })
  })
})

// Tooltip initialization
document.addEventListener("DOMContentLoaded", () => {
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  const bootstrap = window.bootstrap // Declare the bootstrap variable
  tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
})

// Confirmation dialogs for dangerous actions
document.addEventListener("DOMContentLoaded", () => {
  const dangerousActions = document.querySelectorAll("[data-confirm]")
  dangerousActions.forEach((element) => {
    element.addEventListener("click", function (e) {
      const message = this.getAttribute("data-confirm")
      if (!confirm(message)) {
        e.preventDefault()
      }
    })
  })
})

document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', () => {
        const targetId = button.getAttribute('data-target');
        const input = document.getElementById(targetId);
        const icon = button.querySelector('i');
        if (input.type === "password") {
            input.type = "text";
            icon.className = "fas fa-eye-slash";
        } else {
            input.type = "password";
            icon.className = "fas fa-eye";
        }
    });
});
