// Submits the search form when the sort order changes. Without JavaScript the "Apply sort" button is used instead.
document.querySelectorAll('[data-sort-select]').forEach(($select) => {
  $select.addEventListener('change', () => $select.form.submit())
})
