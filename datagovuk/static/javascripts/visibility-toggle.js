class DatagovukVisibilityToggle {
  constructor($button) {
    this.$button = $button
    this.showText = this.$button.textContent
    this.hideText = this.$button.getAttribute("data-hide-text") || "Hide"
    this.$showTarget = document.querySelector("#" + this.$button.getAttribute("aria-controls"))
    if (!this.$showTarget) {
      console.error('DatagovukVisibilityToggle - Elements not found')
      return
    }
    this.showDisplayValue = this.getShowDisplayValue()
    this.$showTarget.style.display = "none";
    this.$button.setAttribute("aria-expanded", "false")
    this.$button.addEventListener("click", () => this.toggle())
  }

  getShowDisplayValue() {
    if (this.$showTarget.tagName == "TBODY") {
      return "table-row-group"
    }
    return "block"
  }

  toggle() {
    if (this.$button.getAttribute("aria-expanded") == "false") {
      this.$showTarget.style.display = this.showDisplayValue
      this.$button.setAttribute("aria-expanded", "true")
      this.$button.textContent = this.hideText
    }
    else {
      this.$showTarget.style.display = "none"
      this.$button.setAttribute("aria-expanded", "false")
      this.$button.textContent = this.showText
    }
  }
}

// Initialize
const $buttons = document.querySelectorAll('.datagovuk-visibility-toggle')
$buttons.forEach(($button, index) => {
  new DatagovukVisibilityToggle($button)
});
