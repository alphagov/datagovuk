// Filters a facet group's values as the user types. Searches all values, including those behind "Show more".
// The search box is hidden in the HTML and only revealed here, so it never appears without JavaScript.
class DatagovukFacetSearch {
  // Screen readers echo every keystroke, so a short delay would be cut off mid-word
  static ANNOUNCE_DELAY = 1000

  constructor($group) {
    this.$group = $group
    this.$search = $group.querySelector('[data-facet-search]')
    this.$input = this.$search.querySelector('input')
    this.$empty = this.$search.querySelector('[data-facet-search-empty]')
    this.$live = this.$search.querySelector('[data-facet-search-live]')
    this.$items = Array.from($group.querySelectorAll('[data-facet-label]'))
    this.$toggle = $group.querySelector('.datagovuk-visibility-toggle')
    this.$rest = this.$toggle && document.getElementById(this.$toggle.getAttribute('aria-controls'))
    this.$scroll = $group.querySelector('.datagovuk-search-facets-wrapper')
    this.timer = null
    this.lastCount = null

    this.$search.hidden = false
    this.$input.addEventListener('input', () => this.filter())
  }

  filter() {
    const term = this.$input.value.trim().toLowerCase()
    clearTimeout(this.timer)

    if (!term) {
      this.$items.forEach(($item) => { $item.hidden = false })
      this.$empty.hidden = true
      this.$live.textContent = ''
      this.lastCount = null
      this.setFiltering(false)
      return
    }

    this.setFiltering(true)
    // Otherwise matches can sit above the visible part of a scrolled list
    this.$scroll.scrollTop = 0
    let matches = 0
    this.$items.forEach(($item) => {
      const matched = $item.dataset.facetLabel.toLowerCase().includes(term)
      $item.hidden = !matched
      if (matched) matches++
    })
    this.$empty.hidden = matches > 0

    if (matches === this.lastCount) return
    this.timer = setTimeout(() => {
      this.lastCount = matches
      this.$live.textContent = matches === 0 ? this.$empty.textContent : matches === 1 ? '1 result' : `${matches} results`
    }, DatagovukFacetSearch.ANNOUNCE_DELAY)
  }

  // While a term is active the "Show more" list is always open and its button is out of the way
  setFiltering(filtering) {
    if (!this.$toggle || !this.$rest) return
    if (filtering) {
      this.$rest.style.display = 'block'
      this.$toggle.style.display = 'none'
    } else {
      const expanded = this.$toggle.getAttribute('aria-expanded') === 'true'
      this.$rest.style.display = expanded ? 'block' : 'none'
      this.$toggle.style.display = ''
    }
  }
}

document.querySelectorAll('[data-facet-group]').forEach(($group) => {
  if ($group.querySelector('[data-facet-search]')) new DatagovukFacetSearch($group)
})
