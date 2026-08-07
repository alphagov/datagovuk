class DatagovukVisibilityToggle {
  constructor($button) {
    this.$button = $button
    this.$showTarget = document.querySelector("#" + this.$button.getAttribute("aria-controls"))
    this.showDisplayValue = this.getShowDisplayValue()
    this.$showTarget.style.display = "none";
    this.$button.setAttribute("aria-expanded", "false")
    this.$button.addEventListener("click", () => this.toggle())
  }

  getShowDisplayValue() {
    if (this.$showTarget.tagName == "tbody") {
      return "table-row-group"
    }
    return "block"
  }

  toggle() {
    if (this.$button.getAttribute("aria-expanded") == "false") {
      this.$showTarget.style.display = this.showDisplayValue
      this.$button.setAttribute("aria-expanded", "true")
      this.$button.textContent = "Show less"
    }
    else {
      this.$showTarget.style.display = "none"
      this.$button.setAttribute("aria-expanded", "false")
      this.$button.textContent = "Show more"
    }
  }
}

// Initialize
const $buttons = document.querySelectorAll('.datagovuk-visibility-toggle')
$buttons.forEach(($button, index) => {
  new DatagovukVisibilityToggle($button)
});
