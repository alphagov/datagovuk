// Replaces the browser's own dropdown list with a styled one, keeping the real <select> in the form.
// Markup: a [data-custom-select] container holding a <label> and a <select>.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-custom-select]').forEach((container) => {
    const select = container.querySelector('select')
    const label = container.querySelector('label')
    if (!select || !label) return

    const id = select.id
    const button = document.createElement('button')
    button.type = 'button'
    button.className = 'datagovuk-select__button'
    button.id = `${id}-button`
    button.setAttribute('aria-haspopup', 'listbox')
    button.setAttribute('aria-expanded', 'false')
    button.setAttribute('aria-controls', `${id}-list`)
    button.setAttribute('aria-labelledby', `${label.id || (label.id = `${id}-label`)} ${button.id}`)

    const list = document.createElement('ul')
    list.className = 'datagovuk-select__list'
    list.id = `${id}-list`
    list.setAttribute('role', 'listbox')
    list.setAttribute('aria-labelledby', label.id)
    list.tabIndex = -1
    list.hidden = true

    const options = [...select.options].map((option, index) => {
      const item = document.createElement('li')
      item.className = 'datagovuk-select__option'
      item.id = `${id}-option-${index}`
      item.setAttribute('role', 'option')
      item.dataset.value = option.value
      item.textContent = option.textContent
      list.append(item)
      return item
    })

    const wrapper = document.createElement('div')
    wrapper.className = 'datagovuk-select'
    wrapper.append(button, list)
    select.after(wrapper)
    select.classList.add('govuk-visually-hidden')
    select.tabIndex = -1
    select.setAttribute('aria-hidden', 'true')
    label.htmlFor = button.id

    let active = select.selectedIndex

    const render = () => {
      button.textContent = select.options[select.selectedIndex].textContent
      options.forEach((item, index) => {
        item.setAttribute('aria-selected', String(index === select.selectedIndex))
        item.classList.toggle('is-active', index === active)
      })
      if (!list.hidden) list.setAttribute('aria-activedescendant', options[active].id)
    }

    const open = () => {
      active = select.selectedIndex
      list.hidden = false
      button.setAttribute('aria-expanded', 'true')
      render()
      list.focus()
    }

    const close = (returnFocus = true) => {
      list.hidden = true
      button.setAttribute('aria-expanded', 'false')
      list.removeAttribute('aria-activedescendant')
      if (returnFocus) button.focus()
    }

    const choose = (index) => {
      const changed = index !== select.selectedIndex
      select.selectedIndex = index
      close()
      render()
      // Lets the form react exactly as it does to a native choice (e.g. re-run the search)
      if (changed) select.dispatchEvent(new Event('change', { bubbles: true }))
    }

    button.addEventListener('click', () => (list.hidden ? open() : close()))
    button.addEventListener('keydown', (event) => {
      if (['ArrowDown', 'ArrowUp'].includes(event.key)) {
        event.preventDefault()
        open()
      }
    })

    list.addEventListener('click', (event) => {
      const index = options.indexOf(event.target.closest('[role="option"]'))
      if (index !== -1) choose(index)
    })
    list.addEventListener('mousemove', (event) => {
      const index = options.indexOf(event.target.closest('[role="option"]'))
      if (index !== -1 && index !== active) {
        active = index
        render()
      }
    })
    list.addEventListener('keydown', (event) => {
      const last = options.length - 1
      const moves = { ArrowDown: Math.min(active + 1, last), ArrowUp: Math.max(active - 1, 0), Home: 0, End: last }
      if (event.key in moves) {
        event.preventDefault()
        active = moves[event.key]
        render()
      } else if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault()
        choose(active)
      } else if (event.key === 'Escape') {
        event.preventDefault()
        close()
      } else if (event.key === 'Tab') {
        close(false)
      }
    })

    document.addEventListener('click', (event) => {
      if (!list.hidden && !wrapper.contains(event.target)) close(false)
    })

    render()
  })
})
