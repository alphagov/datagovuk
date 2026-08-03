class DatagovukShowMore {
  constructor($button) {
    this.$button = $button
    this.$showTarget = document.querySelector("#" + this.$button.getAttribute("aria-controls"))
    this.displayValue = this.$button.getAttribute("data-show-display") || "block"
    this.truncatedEndId = this.$button.getAttribute("data-truncated-end")
    if (this.truncatedEndId) {
      this.$truncatedEnd = document.querySelector("#" + this.truncatedEndId);
    }
    this.$showTarget.style.display = "none";
    this.$button.setAttribute("aria-expanded", "false")
    this.$button.addEventListener("click", () => this.toggle())
  }

  toggle() {
    if (this.$button.getAttribute("aria-expanded") == "false") {
      this.$showTarget.style.display = this.displayValue
      this.hideEnd()
      this.$button.setAttribute("aria-expanded", "true")
      this.$button.textContent = "Show less"
    }
    else {
      this.$showTarget.style.display = "none"
      this.showEnd()
      this.$button.setAttribute("aria-expanded", "false")
      this.$button.textContent = "Show more"
    }
  }

  hideEnd() {
    if (this.truncatedEndId) {
      this.$truncatedEnd.style.display = "none"
    }
  }

  showEnd() {
    if (this.truncatedEndId) {
      this.$truncatedEnd.style.display = "inline"
    }
  }
}

// Initialize
const $buttons = document.querySelectorAll('.datagovuk-show-more')
$buttons.forEach(($button, index) => {
  new DatagovukShowMore($button)
});
