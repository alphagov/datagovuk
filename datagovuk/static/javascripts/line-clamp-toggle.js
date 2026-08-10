class DatagovukLineClampToggle {
  constructor($button) {
    this.$button = $button
    this.$showTarget = document.querySelector("#" + this.$button.getAttribute("aria-controls"))
    this.clampClass = "datagovuk-line-clamp"
    this.$showTarget.classList.add(this.clampClass)

    if (this.$showTarget.scrollHeight <= this.$showTarget.clientHeight) {
      this.$button.style.display = "none"
      return
    }

    this.$button.setAttribute("aria-expanded", "false")
    this.$button.addEventListener("click", () => this.toggle())
  }

  toggle() {
    const isExpanded = this.$button.getAttribute("aria-expanded") === "true"

    if (isExpanded) {
      this.$showTarget.classList.add(this.clampClass)
      this.$button.setAttribute("aria-expanded", "false")
      this.$button.textContent = "Show more"
    } else {
      this.$showTarget.classList.remove(this.clampClass)
      this.$button.setAttribute("aria-expanded", "true")
      this.$button.textContent = "Show less"
    }
  }
}

// Initialize
const $clampButtons = document.querySelectorAll('.datagovuk-line-clamp-toggle')
$clampButtons.forEach(($button) => {
  new DatagovukLineClampToggle($button)
})
