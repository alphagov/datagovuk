// A button that shows and hides a panel on mobile, e.g. the search filters.
//
// Markup:
//   <div data-subnav>
//     <button type="button" data-subnav-button aria-controls="panel-id">...</button>
//     <div id="panel-id" data-subnav-panel>...</div>
//   </div>
//
// Starts closed. Closes on Escape, on a click outside, and when focus moves outside. Without JavaScript the button
// is hidden by CSS and the panel stays visible. Desktop styles keep the panel visible even when it is closed.
class DatagovukSubnav {
  constructor($subnav) {
    this.$subnav = $subnav
    this.$button = $subnav.querySelector('[data-subnav-button]')
    this.$panel = $subnav.querySelector('[data-subnav-panel]')

    this.close()
    this.$button.addEventListener('click', () => this.toggle())

    document.addEventListener('keydown', (event) => this.handleKeydown(event))

    // Close when focus moves to something outside the subnav (e.g. tabbing out)
    document.addEventListener('focusin', (event) => {
      if (!this.$subnav.contains(event.target)) this.close()
    })

    // Close when clicking outside the subnav
    document.addEventListener('click', (event) => {
      if (!this.$subnav.contains(event.target)) this.close()
    })
  }

  isOpen() {
    return this.$button.getAttribute('aria-expanded') === 'true'
  }

  toggle() {
    if (this.isOpen()) this.close()
    else this.open()
  }

  open() {
    this.$panel.hidden = false
    this.$button.setAttribute('aria-expanded', 'true')
  }

  close() {
    this.$panel.hidden = true
    this.$button.setAttribute('aria-expanded', 'false')
  }

  handleKeydown(event) {
    if (event.key === 'Escape' && this.isOpen()) {
      this.close()
      this.$button.focus()
    }
  }
}

document.querySelectorAll('[data-subnav]').forEach(($subnav) => new DatagovukSubnav($subnav))
