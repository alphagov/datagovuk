// Tooltips can be dismissed with Escape without moving focus, and come back next time they are hovered or focused.
document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return
  document.querySelectorAll('.datagovuk-tooltip').forEach((tooltip) => tooltip.classList.add('is-dismissed'))
})

document.querySelectorAll('.datagovuk-tooltip').forEach((tooltip) => {
  const reset = () => tooltip.classList.remove('is-dismissed')
  tooltip.addEventListener('mouseleave', reset)
  tooltip.addEventListener('focusout', reset)
})
