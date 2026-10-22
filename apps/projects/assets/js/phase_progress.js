const PHASE_PROGRESS_SELECTOR = '[data-phase-progress]'
const PHASE_PROGRESS_INTERVAL = 1000

function phaseProgressPercent (start, end, now) {
  const total = end - start
  if (!Number.isFinite(total) || total <= 0) {
    return null
  }
  const elapsed = now - start
  return Math.min(100, Math.max(0, (elapsed / total) * 100))
}

function updatePhaseProgress (element, now = Date.now()) {
  const start = Date.parse(element.dataset.phaseStart)
  const end = Date.parse(element.dataset.phaseEnd)
  const percent = phaseProgressPercent(start, end, now)
  if (percent === null) {
    return
  }

  const fill = element.querySelector('.phase-stepper__progress-fill')
  if (fill) {
    fill.style.width = `${percent}%`
  }
  element.setAttribute('aria-valuenow', String(Math.round(percent)))
}

function initPhaseProgress () {
  const bars = document.querySelectorAll(PHASE_PROGRESS_SELECTOR)
  if (!bars.length) {
    return
  }

  const updateAll = () => {
    bars.forEach((bar) => updatePhaseProgress(bar))
  }

  updateAll()

  const interval = window.setInterval(updateAll, PHASE_PROGRESS_INTERVAL)
  window.addEventListener('pagehide', () => window.clearInterval(interval))
}

export { initPhaseProgress, phaseProgressPercent, updatePhaseProgress }
