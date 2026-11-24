document.addEventListener("DOMContentLoaded", () => {
  // Mobile Navigation Toggle
  const navToggle = document.getElementById("navToggle");
  const navLinks = document.getElementById("navLinks");
  if (navToggle && navLinks) {
    navToggle.addEventListener("click", () => {
      navLinks.classList.toggle("open");
    });
  }

  // Donation Preset Amount Buttons
  const presetButtons = document.querySelectorAll(".preset-btn");
  const amountInput = document.getElementById("donationAmount");
  if (presetButtons.length && amountInput) {
    presetButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        presetButtons.forEach((b) => b.classList.remove("selected"));
        btn.classList.add("selected");
        amountInput.value = btn.dataset.amount;
      });
    });
    amountInput.addEventListener("input", () => {
      presetButtons.forEach((b) => b.classList.remove("selected"));
    });
  }

  // Form Loading State on Submit
  const forms = document.querySelectorAll("form[data-loading]");
  forms.forEach((form) => {
    form.addEventListener("submit", () => {
      const submitBtn = form.querySelector("button[type='submit']");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.originalText = submitBtn.textContent;
        submitBtn.textContent = submitBtn.dataset.loadingText || "Processing...";
      }
    });
  });

  // Client-side file size validation (5 MB)
  const fileInputs = document.querySelectorAll("input[type='file']");
  fileInputs.forEach((input) => {
    input.addEventListener("change", () => {
      const file = input.files[0];
      if (file && file.size > 5 * 1024 * 1024) {
        alert("File exceeds the 5 MB limit. Please choose a smaller file.");
        input.value = "";
      }
    });
  });
});
