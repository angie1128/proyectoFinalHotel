// Theme Management
function toggleTheme() {
  const html = document.documentElement
  const themeIcon = document.getElementById("theme-icon")
  const currentTheme = html.getAttribute("data-theme")

  if (currentTheme === "dark") {
    html.setAttribute("data-theme", "light")
    themeIcon.className = "fas fa-sun"
    localStorage.setItem("theme", "light")
  } else {
    html.setAttribute("data-theme", "dark")
    themeIcon.className = "fas fa-moon"
    localStorage.setItem("theme", "dark")
  }
}

// Load saved theme on page load
document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light"
  const html = document.documentElement
  const themeIcon = document.getElementById("theme-icon")

  html.setAttribute("data-theme", savedTheme)

  if (savedTheme === "dark") {
    themeIcon.className = "fas fa-moon"
  } else {
    themeIcon.className = "fas fa-sun"
  }
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
