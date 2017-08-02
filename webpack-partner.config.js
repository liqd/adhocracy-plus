var ExtractTextPlugin = require('extract-text-webpack-plugin')
var path = require('path')
var autoprefixer = require('autoprefixer')

var config = {
  entry: {
    adhocracy4: [
      './liqd_product/assets/scss/style.scss'
    ]
  },
  devtool: 'eval',
  output: {
    libraryTarget: 'this',
    library: '[name]',
    path: path.resolve('./liqd_product/static/'),
    publicPath: '/static/',
    filename: `styles_${process.env.PARTNER_SLUG}.js`
  },
  module: {
    loaders: [
      {
        test: /\.s?css$/,
        loader: ExtractTextPlugin.extract('style?sourceMap', '!css?sourceMap!postcss?sourceMap!sass?sourceMap')
      },
      {
        test: /fonts\/.*\.(svg|woff2?|ttf|eot|otf)(\?.*)?$/,
        loader: 'file-loader?name=fonts/[name].[ext]'
      },
      {
        test: /\.svg$|\.png$/,
        loader: 'file-loader?name=images/[name].[ext]'
      }
    ]
  },
  postcss: [
    autoprefixer({browsers: ['last 3 versions', 'ie >= 10']})
  ],
  resolve: {
    extensions: ['', '.js', '.jsx', '.scss', '.css'],
    alias: {
      'jquery$': 'jquery/dist/jquery.min.js'
    },
    // when using `npm link`, dependencies are resolved against the linked
    // folder by default. This may result in dependencies being included twice.
    // Setting `resolve.root` forces webpack to resolve all dependencies
    // against the local directory.
    root: path.resolve('./node_modules')
  },
  resolveLoader: {
    root: path.resolve('./node_modules')
  },
  plugins: [
    new ExtractTextPlugin(`styles_${process.env.PARTNER_SLUG}.css`)
  ]
}

if (process.env.PARTNER_HEX) {
  config.sassLoader = {
    data: `$brand-primary: #${process.env.PARTNER_HEX};`
  }
}

module.exports = config
