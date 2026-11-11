class DatagovukSectionNavigation {
  constructor($sectionNavigation) {
    this.$sectionNavigation = $sectionNavigation
    this.$button = $sectionNavigation.querySelector('#datagovuk-section-navigation-button-all')
    this.$navigationItems = $sectionNavigation.querySelector('.datagovuk-section-navigation__items-mobile')

    this.$button.setAttribute('aria-expanded', 'false')

    // Toggle on button click (stop propagation so the document click listener doesn't immediately catch it)
    this.$button.addEventListener('click', (event) => {
      event.stopPropagation()
      this.toggleNavigationItems()
    })

    // Clicking anywhere inside the navigation items shouldn't close it
    this.$navigationItems.addEventListener('click', (event) => {
      event.stopPropagation()
    })

    this.close()

    // Document-level click handler to close when clicking outside
    document.addEventListener('click', () => {
      this.close()
    })

    // Keep keyboard accessibility (Escape key and tabbing out)
    document.addEventListener('keydown', (event) => this.handleKeydown(event))
  }

  toggleNavigationItems() {
    const shouldOpen = this.$button.getAttribute('aria-expanded') === 'false'
    this.close()

    if (shouldOpen) {
      this.$button.setAttribute('aria-expanded', 'true')
      this.$navigationItems.hidden = false
    }
  }

  close() {
    this.$navigationItems.hidden = true
    this.$button.setAttribute('aria-expanded', 'false')
  }

  handleKeydown(event) {
    if (event.key === 'Escape') {
      const $openButton = [this.$button].find(
        $button => $button.getAttribute('aria-expanded') === 'true'
      )

      if ($openButton) {
        this.close()
        $openButton.focus()
      }
    }
  }
}

// Initialize
const $sectionNavigation = document.querySelector('.datagovuk-section-navigation')
if ($sectionNavigation) {
  new DatagovukSectionNavigation($sectionNavigation)
}
