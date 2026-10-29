/**
 * Dashboard-only initialisation (loaded from a4dashboard/base_dashboard.html).
 */
import { initAddedModuleFocus, initDashboardAccordion } from './dashboard_accordion.js'
import { initCkeditorFontSizeAsHeadings } from './ckeditor-fontsize-as-headings.js'

document.addEventListener('DOMContentLoaded', () => {
  initDashboardAccordion()
  initAddedModuleFocus()
  initCkeditorFontSizeAsHeadings()
}, false)
