// Main JavaScript functionality
document.addEventListener("DOMContentLoaded", () => {
  // Initialize date inputs
  initializeDateInputs()

  // Initialize room availability checker
  initializeAvailabilityChecker()

  // Initialize smooth scrolling
  initializeSmoothScrolling()

  // Initialize form validations
  initializeFormValidations()
})

function initializeDateInputs() {
  const checkinInput = document.getElementById("checkin")
  const checkoutInput = document.getElementById("checkout")

  if (checkinInput && checkoutInput) {
    // Set minimum date to today
    const today = new Date().toISOString().split("T")[0]
    checkinInput.min = today

    // Update checkout minimum when checkin changes
    checkinInput.addEventListener("change", function () {
      const checkinDate = new Date(this.value)
      checkinDate.setDate(checkinDate.getDate() + 1)
      checkoutInput.min = checkinDate.toISOString().split("T")[0]

      // Clear checkout if it's before new minimum
      if (checkoutInput.value && checkoutInput.value <= this.value) {
        checkoutInput.value = ""
      }
    })
  }
}

function initializeAvailabilityChecker() {
  const searchButton = document.querySelector(".booking-widget .btn-gold")

  if (searchButton) {
    searchButton.addEventListener("click", (e) => {
      e.preventDefault()

      const checkin = document.getElementById("checkin").value
      const checkout = document.getElementById("checkout").value
      const guests = document.querySelector(".booking-widget select").value

      if (!checkin || !checkout) {
        showAlert("Por favor selecciona las fechas de llegada y salida", "warning")
        return
      }

      if (new Date(checkin) >= new Date(checkout)) {
        showAlert("La fecha de salida debe ser posterior a la fecha de llegada", "warning")
        return
      }

      // Redirect to rooms page with parameters
      const params = new URLSearchParams({
        checkin: checkin,
        checkout: checkout,
        guests: guests,
      })

      window.location.href = `/rooms?${params.toString()}`
    })
  }
}

function initializeSmoothScrolling() {
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
}

function initializeFormValidations() {
  // Real-time form validation
  const forms = document.querySelectorAll("form")

  forms.forEach((form) => {
    const inputs = form.querySelectorAll("input[required]")

    inputs.forEach((input) => {
      input.addEventListener("blur", function () {
        validateInput(this)
      })

      input.addEventListener("input", function () {
        if (this.classList.contains("is-invalid")) {
          validateInput(this)
        }
      })
    })

    form.addEventListener("submit", (e) => {
      let isValid = true

      inputs.forEach((input) => {
        if (!validateInput(input)) {
          isValid = false
        }
      })

      if (!isValid) {
        e.preventDefault()
        showAlert("Por favor corrige los errores en el formulario", "error")
      }
    })
  })
}

function validateInput(input) {
  const value = input.value.trim()
  let isValid = true
  let message = ""

  // Required validation
  if (input.hasAttribute("required") && !value) {
    isValid = false
    message = "Este campo es obligatorio"
  }

  // Email validation
  if (input.type === "email" && value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      isValid = false
      message = "Ingresa un email válido"
    }
  }

  // Password validation
  if (input.type === "password" && value) {
    if (value.length < 6) {
      isValid = false
      message = "La contraseña debe tener al menos 6 caracteres"
    }
  }

  // Phone validation
  if (input.type === "tel" && value) {
    const phoneRegex = /^[+]?[1-9][\d]{0,15}$/
    if (!phoneRegex.test(value.replace(/[\s\-$$$$]/g, ""))) {
      isValid = false
      message = "Ingresa un número de teléfono válido"
    }
  }

  // Update UI
  if (isValid) {
    input.classList.remove("is-invalid")
    input.classList.add("is-valid")
    removeErrorMessage(input)
  } else {
    input.classList.remove("is-valid")
    input.classList.add("is-invalid")
    showErrorMessage(input, message)
  }

  return isValid
}

function showErrorMessage(input, message) {
  removeErrorMessage(input)

  const errorDiv = document.createElement("div")
  errorDiv.className = "invalid-feedback"
  errorDiv.textContent = message

  input.parentNode.appendChild(errorDiv)
}

function removeErrorMessage(input) {
  const existingError = input.parentNode.querySelector(".invalid-feedback")
  if (existingError) {
    existingError.remove()
  }
}

function showAlert(message, type = "info") {
  // Create alert element
  const alertDiv = document.createElement("div")
  alertDiv.className = `alert alert-${type === "error" ? "danger" : type} alert-dismissible fade show`
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  // Insert at top of main content
  const container = document.querySelector(".container")
  if (container) {
    container.insertBefore(alertDiv, container.firstChild)

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      if (alertDiv.parentNode) {
        alertDiv.remove()
      }
    }, 5000)
  }
}

// Room availability checker
function checkRoomAvailability(roomId, checkin, checkout) {
  return fetch(`/api/check-availability?room_id=${roomId}&check_in=${checkin}&check_out=${checkout}`)
    .then((response) => response.json())
    .then((data) => {
      return data.available
    })
    .catch((error) => {
      console.error("Error checking availability:", error)
      return false
    })
}

// Booking form handler
function handleBookingForm() {
  const bookingForm = document.getElementById("booking-form")

  if (bookingForm) {
    bookingForm.addEventListener("submit", function (e) {
      e.preventDefault()

      const formData = new FormData(this)
      const submitButton = this.querySelector('button[type="submit"]')

      // Disable submit button
      submitButton.disabled = true
      submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...'

      fetch("/booking/create", {
        method: "POST",
        body: formData,
      })
        .then((response) => {
          if (response.ok) {
            showAlert("¡Reserva creada exitosamente!", "success")
            setTimeout(() => {
              window.location.href = "/booking/my-bookings"
            }, 2000)
          } else {
            throw new Error("Error en la reserva")
          }
        })
        .catch((error) => {
          showAlert("Error al crear la reserva. Inténtalo de nuevo.", "error")
          console.error("Booking error:", error)
        })
        .finally(() => {
          // Re-enable submit button
          submitButton.disabled = false
          submitButton.innerHTML = '<i class="fas fa-calendar-check me-2"></i>Confirmar Reserva'
        })
    })
  }
}

// Initialize booking form when page loads
document.addEventListener("DOMContentLoaded", handleBookingForm)

// Utility functions
function formatCurrency(amount) {
  return new Intl.NumberFormat("es-ES", {
    style: "currency",
    currency: "USD",
  }).format(amount)
}

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString("es-ES", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}

// Loading animation
function showLoading() {
  const loadingDiv = document.createElement("div")
  loadingDiv.id = "loading-overlay"
  loadingDiv.innerHTML = `
        <div class="d-flex justify-content-center align-items-center h-100">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `
  loadingDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        z-index: 9999;
    `

  document.body.appendChild(loadingDiv)
}

function hideLoading() {
  const loadingDiv = document.getElementById("loading-overlay")
  if (loadingDiv) {
    loadingDiv.remove()
  }
}
