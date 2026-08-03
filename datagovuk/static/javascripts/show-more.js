class DatagovukShowMore {
  constructor($button) {
    this.$button = $button
    this.$showTarget = document.querySelector("#" + this.$button.getAttribute("aria-controls"))
    this.$showTarget.style.display = "none";
    this.$button.setAttribute("aria-expanded", "false")
    this.$button.addEventListener("click", () => this.toggle())
  }

  toggle() {
    if (this.$button.getAttribute("aria-expanded") == "false") {
      this.$showTarget.style.display = "block"
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
const $buttons = document.querySelectorAll('.datagovuk-show-more')
$buttons.forEach(($button, index) => {
  new DatagovukShowMore($button)
});
