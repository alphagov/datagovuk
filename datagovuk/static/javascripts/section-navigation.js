class DatagovukSectionNavigation {
  constructor($sectionNavigation) {
    this.$sectionNavigation = $sectionNavigation
    this.$button = $sectionNavigation.querySelector('#datagovuk-section-navigation-button-all')
    this.$navigationItems = $sectionNavigation.querySelector('.datagovuk-section-navigation__items-mobile')
    
    this.$button.setAttribute('aria-expanded', 'false')
    this.$button.addEventListener('click', () => this.toggleNavigationItems())
    this.close()

    document.addEventListener('keydown', (event) => this.handleKeydown(event))

    // Close when focus moves to something outside the navigation (e.g. tabbing out)
    document.addEventListener('focusin', (event) => {
      if (this.$sectionNavigation.contains(event.target) === false) this.close()
    })

    // Close when clicking outside the navigation
    document.addEventListener('click', (event) => {
      if (this.$sectionNavigation.contains(event.target) === false) this.close()
    })
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
      const isOpen = this.$button.getAttribute('aria-expanded') === 'true'
      if (isOpen) {
        this.close()
        this.$button.focus()
      }
    }
  }
}

// Initialize
const $sectionNavigation = document.querySelector('.datagovuk-section-navigation')
if ($sectionNavigation) {
  new DatagovukSectionNavigation($sectionNavigation)
}