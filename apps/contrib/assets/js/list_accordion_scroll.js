/**
 * Scroll list cards into view when their accordion state changes on mobile.
 *
 * Used by the ideas and mapideas card lists.
 * - Expanding: scroll the card into view unless it is already fully visible.
 *   With an accordion parent, opening one card collapses the previously open
 *   one; that collapse shifts the target's position, so the scroll waits until
 *   the expansion and any sibling collapse have finished.
 * - Collapsing: if the user has scrolled past the card's top, bring it back
 *   into view so they don't end up looking at content that shifted up.
 */

const desktop = window.matchMedia('(min-width: 768px)')
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
const SCROLL_GAP = 16
const SETTLE_FALLBACK_DELAY = 700

// Offset the sticky submit call to action (when present), plus a small gap.
function getScrollOffset () {
  const stickyCta = document.querySelector('.sticky-cta__inner')
  if (stickyCta) {
    const row = stickyCta.closest('.project-detail__module-action-row')
    if (row && window.getComputedStyle(row).position === 'sticky') {
      return row.getBoundingClientRect().height + SCROLL_GAP
    }
  }
  return SCROLL_GAP
}

function isFullyVisible (item, offset) {
  const rect = item.getBoundingClientRect()
  return rect.top >= offset && rect.bottom <= window.innerHeight
}

function scrollToItem (item) {
  const offset = getScrollOffset()
  if (isFullyVisible(item, offset)) {
    return
  }
  item.style.scrollMarginTop = offset + 'px'
  item.scrollIntoView({
    behavior: reducedMotion.matches ? 'auto' : 'smooth',
    block: 'start'
  })
}

function isTopVisible (item, offset) {
  const rect = item.getBoundingClientRect()
  return rect.top >= offset && rect.top < window.innerHeight
}

// Bring the card's top back into view (used when collapsing a card the user
// has scrolled past, so they don't end up looking at shifted content).
function scrollTopIntoView (item) {
  const offset = getScrollOffset()
  if (isTopVisible(item, offset)) {
    return
  }
  item.style.scrollMarginTop = offset + 'px'
  item.scrollIntoView({
    behavior: reducedMotion.matches ? 'auto' : 'smooth',
    block: 'start'
  })
}

export function initListAccordionScroll (accordion) {
  if (!accordion) {
    return
  }

  let pendingItem = null
  let expansionPending = false
  let siblingPending = false
  let fallbackTimeout = null

  function settle () {
    if (!pendingItem || expansionPending || siblingPending) {
      return
    }
    const item = pendingItem
    pendingItem = null
    clearTimeout(fallbackTimeout)
    scrollToItem(item)
  }

  function startFallback () {
    clearTimeout(fallbackTimeout)
    // Fallback in case a shown/hidden event never fires.
    fallbackTimeout = setTimeout(function () {
      expansionPending = false
      siblingPending = false
      settle()
    }, SETTLE_FALLBACK_DELAY)
  }

  accordion.addEventListener('show.bs.collapse', function (event) {
    if (desktop.matches) {
      return
    }
    const item = event.target.closest('.list-item')
    if (!item) {
      return
    }
    pendingItem = item
    expansionPending = true

    const openSibling = Array.prototype.find.call(
      accordion.querySelectorAll('.collapse'),
      function (el) {
        return el !== event.target &&
          (el.classList.contains('show') || el.classList.contains('collapsing'))
      }
    )
    siblingPending = !!openSibling
    startFallback()
    settle()
  })

  // When a card is collapsed directly (not the auto-collapse triggered by
  // opening another card), keep its top in view if the user has scrolled past
  // it, so they don't end up looking at content that shifted up.
  accordion.addEventListener('hide.bs.collapse', function (event) {
    if (desktop.matches) {
      return
    }
    const item = event.target.closest('.list-item')
    if (!item) {
      return
    }
    if (pendingItem === item) {
      // The card was still expanding and is being collapsed again.
      pendingItem = null
      expansionPending = false
      siblingPending = false
      clearTimeout(fallbackTimeout)
      return
    }
    if (pendingItem) {
      // Auto-collapse while another card is being expanded.
      return
    }
    scrollTopIntoView(item)
  })

  accordion.addEventListener('shown.bs.collapse', function (event) {
    if (!pendingItem) {
      return
    }
    const item = event.target.closest('.list-item')
    if (item === pendingItem) {
      expansionPending = false
      settle()
    }
  })

  accordion.addEventListener('hidden.bs.collapse', function () {
    siblingPending = false
    settle()
  })
}

export function initAllListAccordionScroll () {
  document.querySelectorAll('[data-accordion-scroll]').forEach(function (accordion) {
    initListAccordionScroll(accordion)
  })
}

document.addEventListener('DOMContentLoaded', initAllListAccordionScroll)
