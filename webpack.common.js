const webpack = require('webpack')
const path = require('path')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

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
      'js-cookie',
      'line-awesome/css/line-awesome.min.css',
      'react',
      'immutability-helper',
      'react-dom',
      'react-flip-move',
      'typeface-libre-franklin'
    ],
    leaflet: [
      'leaflet',
      'mapbox-gl-leaflet',
      'mapbox-gl/dist/mapbox-gl.js',
      'mapbox-gl/dist/mapbox-gl.css',
      'leaflet/dist/leaflet.css',
      'leaflet.markercluster',
      'leaflet.markercluster/dist/MarkerCluster.css'
    ],
    embed: [
      './liqd_product/assets/js/embed.js'
    ],
    'popup-close': [
      './liqd_product/assets/js/popup-close.js'
    ],
    'map_choose_polygon_with_preset': [
      './liqd_product/apps/maps/assets/map_choose_polygon_with_preset.js',
      'leaflet-draw',
      'leaflet-draw/dist/leaflet.draw.css',
      './liqd_product/assets/js/i18n-leaflet-draw.js',
      'file-saver',
      'shpjs'
    ]
  },
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
        exclude: /node_modules\/(?!(adhocracy4|bootstrap)\/).*/, // exclude all dependencies but adhocracy4 and bootstrap
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-env', '@babel/preset-react'].map(require.resolve),
          plugins: ['@babel/plugin-transform-runtime', '@babel/plugin-transform-modules-commonjs']
        }
      },
      {
        test: /\.s?css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'sass-loader'
        ]
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
      'shariff$': 'shariff/dist/shariff.min.js'
    },
    // when using `npm link`, dependencies are resolved against the linked
    // folder by default. This may result in dependencies being included twice.
    // Setting `resolve.root` forces webpack to resolve all dependencies
    // against the local directory.
    modules: [path.resolve('./node_modules')]
  },
  plugins: [
    new webpack.ProvidePlugin({
      timeago: 'timeago.js',
      $: 'jquery',
      jQuery: 'jquery'
    }),
    new webpack.optimize.SplitChunksPlugin({
      name: 'vendor',
      filename: 'vendor.js'
    }),
    new MiniCssExtractPlugin({
      filename: '[name].css',
      chunkFilename: '[id].css'
    }),
    new CopyWebpackPlugin([
      {
        from: './liqd_product/assets/images/**/*',
        to: 'images/',
        flatten: true
      }
    ])
  ]
}
