import { phaseProgressPercent, updatePhaseProgress } from './phase_progress.js'

describe('phaseProgressPercent', () => {
  it('computes the elapsed percentage', () => {
    expect(phaseProgressPercent(0, 100, 50)).toBe(50)
  })

  it('clamps the percentage between 0 and 100', () => {
    expect(phaseProgressPercent(0, 100, -10)).toBe(0)
    expect(phaseProgressPercent(0, 100, 200)).toBe(100)
  })

  it('returns null for an invalid window', () => {
    expect(phaseProgressPercent(0, 0, 10)).toBeNull()
    expect(phaseProgressPercent(100, 0, 10)).toBeNull()
    expect(phaseProgressPercent(NaN, 100, 10)).toBeNull()
  })
})

describe('updatePhaseProgress', () => {
  it('sets the fill width and aria-valuenow', () => {
    document.body.innerHTML = `
      <div
        data-phase-progress
        data-phase-start="2020-01-01T00:00:00Z"
        data-phase-end="2020-01-11T00:00:00Z">
        <span class="phase-stepper__progress-fill"></span>
      </div>`

    const element = document.querySelector('[data-phase-progress]')
    const now = Date.parse('2020-01-06T00:00:00Z')

    updatePhaseProgress(element, now)

    expect(element.getAttribute('aria-valuenow')).toBe('50')
    expect(
      element.querySelector('.phase-stepper__progress-fill').style.width
    ).toBe('50%')
  })
})
