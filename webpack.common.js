var ExtractTextPlugin = require('extract-text-webpack-plugin')
var CopyWebpackPlugin = require('copy-webpack-plugin')
var webpack = require('webpack')
var path = require('path')
var autoprefixer = require('autoprefixer')

module.exports = {
  entry: {
    adhocracy4: [
      './liqd_product/assets/scss/style.scss',
      './liqd_product/assets/js/app.js'
    ],
    platform: [
      './liqd_product/assets/scss/platform.scss'
    ],
    vendor: [
      'classnames',
      'jquery',
      'js-cookie',
      'line-awesome/dist/css/line-awesome-font-awesome.css',
      'react',
      'immutability-helper',
      'react-dom',
      'react-flip-move',
      'shariff/dist/shariff.complete.js',
      'shariff/dist/shariff.min.css',
      'typeface-libre-franklin'
    ],
    leaflet: [
      'leaflet',
      'leaflet/dist/leaflet.css',
      'leaflet.markercluster',
      'leaflet.markercluster/dist/MarkerCluster.css'
    ],
    datepicker: [
      './liqd_product/assets/js/init-picker.js',
      'datepicker/css/datepicker.min.css'
    ],
    embed: [
      'a4-meinberlin/meinberlin/assets/js/embed.js'
    ],
    'popup-close': [
      'a4-meinberlin/meinberlin/assets/js/popup-close.js'
    ],
    'map_choose_polygon_with_preset': [
      'a4-meinberlin/meinberlin/apps/maps/assets/map_choose_polygon_with_preset.js',
      'leaflet-draw',
      'leaflet-draw/dist/leaflet.draw.css',
      'a4-meinberlin/meinberlin/assets/js/i18n-leaflet-draw.js',
      'file-saver',
      'shpjs'
    ]
  },
  devtool: 'eval',
  output: {
    libraryTarget: 'this',
    library: '[name]',
    path: path.resolve('./liqd_product/static/'),
    publicPath: '/static/',
    filename: '[name].js'
  },
  externals: {
    'django': 'django'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules\/(?!a4-meinberlin|adhocracy4|bootstrap)/, // exclude all dependencies but meinberlin, adhocracy4 and bootstrap
        loader: 'babel-loader',
        options: {
          presets: ['babel-preset-env', 'babel-preset-react'].map(require.resolve)
        }
      },
      {
        test: /\.s?css$/,
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: [
            'css-loader',
            {
              loader: 'postcss-loader',
              options: {
                ident: 'postcss',
                plugins: (loader) => [
                  autoprefixer()
                ]
              }
            },
            'sass-loader'
          ]
        })
      },
      {
        test: /(fonts|files)\/.*\.(svg|woff2?|ttf|eot|otf)(\?.*)?$/,
        loader: 'file-loader',
        options: {
          name: 'fonts/[name].[ext]'
        }
      },
      {
        test: /\.svg$|\.png$/,
        loader: 'file-loader',
        options: {
          name: 'images/[name].[ext]'
        }
      }
    ]
  },
  resolve: {
    extensions: ['*', '.js', '.jsx', '.scss', '.css'],
    alias: {
      'jquery$': 'jquery/dist/jquery.min.js',
      'shariff$': 'shariff/dist/shariff.complete.js'
    },
    // when using `npm link`, dependencies are resolved against the linked
    // folder by default. This may result in dependencies being included twice.
    // Setting `resolve.root` forces webpack to resolve all dependencies
    // against the local directory.
    modules: [path.resolve('./node_modules')]
  },
  plugins: [
    new webpack.ProvidePlugin({
      timeago: 'timeago.js'
    }),
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',
      filename: 'vendor.js'
    }),
    new ExtractTextPlugin({ filename: '[name].css' }),
    new CopyWebpackPlugin([
      {
        from: './liqd_product/assets/images/**/*',
        to: 'images/',
        flatten: true
      }
    ])
  ]
}
