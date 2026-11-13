// Search inputs show a clear (X) button once something has been typed.
// Markup: a [data-clearable] container holding the input and a [data-clear] button.
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-clearable]').forEach((container) => {
    const input = container.querySelector('input')
    const clear = container.querySelector('[data-clear]')
    if (!input || !clear) return

    input.addEventListener('input', () => {
      container.classList.toggle('is-typing', input.value !== '')
    })

    clear.addEventListener('click', () => {
      input.value = ''
      container.classList.remove('is-typing')
      // Lets anything listening to the input (e.g. the option filter) reset itself
      input.dispatchEvent(new Event('input', { bubbles: true }))
      input.focus()
    })
  })
})
