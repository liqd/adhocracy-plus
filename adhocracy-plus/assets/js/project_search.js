// Client-side search filter for the organisation landing page:
// filters the rendered project tiles by project name without reloading.
function initOrganisationProjectSearch () {
  const container = document.querySelector('[data-project-search]')
  if (!container) {
    return
  }

  const input = container.querySelector('[data-project-search-input]')
  const list = container.querySelector('[data-project-search-list]')
  const empty = container.querySelector('[data-project-search-empty]')
  if (!input || !list || !empty) {
    return
  }

  const tiles = Array.from(list.querySelectorAll('.tile'))

  input.addEventListener('input', function () {
    const query = input.value.trim().toLowerCase()
    let visibleCount = 0

    tiles.forEach(function (tile) {
      const title = tile.querySelector('.tile__title')
      const matches = !query || (title && title.textContent.toLowerCase().includes(query))
      tile.hidden = !matches
      if (matches) {
        visibleCount += 1
      }
    })

    empty.hidden = visibleCount > 0
  })
}

document.addEventListener('DOMContentLoaded', initOrganisationProjectSearch)
