module.exports = {
  gettext: (text) => text,
  pgettext: (context, text) => text,
  ngettext: (singular, plural, count) => count === 1 ? singular : plural,
  interpolate: (fmt, data, named) => {
    if (named) {
      return fmt.replace(/%\((\w+)\)s/g, function (_, k) { return data[k] })
    }
    const values = Object.values(data)
    return values.length > 0 ? String(values[0]) : fmt
  }
}
