const { merge } = require('webpack-merge')
const common = require('./webpack.common.js')

module.exports = merge(common, {
  // controls source mapping to assist in debugging
  mode: 'development',
  devtool: 'eval'
})
