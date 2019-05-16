const webpack = require('webpack')
const path = require('path')
const autoprefixer = require('autoprefixer')
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
      '@fortawesome/fontawesome-free/scss/fontawesome.scss',
      '@fortawesome/fontawesome-free/scss/brands.scss',
      '@fortawesome/fontawesome-free/scss/regular.scss',
      '@fortawesome/fontawesome-free/scss/solid.scss',
      'js-cookie',
      'react',
      'immutability-helper',
      'react-dom',
      'react-flip-move',
      'typeface-libre-franklin'
    ],
    a4maps_display_point: [
      'leaflet/dist/leaflet.css',
      'mapbox-gl/dist/mapbox-gl.css',
      'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_display_point.js'
    ],
    a4maps_display_points: [
      'leaflet/dist/leaflet.css',
      'mapbox-gl/dist/mapbox-gl.css',
      'leaflet.markercluster/dist/MarkerCluster.css',
      'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_display_points.js'
    ],
    a4maps_choose_point: [
      'leaflet/dist/leaflet.css',
      'mapbox-gl/dist/mapbox-gl.css',
      'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_choose_point.js'
    ],
    a4maps_choose_polygon: [
      'leaflet/dist/leaflet.css',
      'mapbox-gl/dist/mapbox-gl.css',
      'leaflet-draw/dist/leaflet.draw.css',
      './apps/maps/assets/map_choose_polygon_with_preset.js'
    ],
    datepicker: [
      './liqd_product/assets/js/init-picker.js',
      'datepicker/css/datepicker.min.css'
    ],
    embed: [
      './liqd_product/assets/js/embed.js'
    ],
    'popup-close': [
      './liqd_product/assets/js/popup-close.js'
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
          {
            loader: MiniCssExtractPlugin.loader
          },
          {
            loader: 'css-loader'
          },
          {
            loader: 'postcss-loader',
            options: {
              ident: 'postcss',
              plugins: (loader) => [
                autoprefixer({ browsers: ['last 3 versions', 'ie >= 11'] })
              ]
            }
          },
          {
            loader: 'sass-loader'
          }
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
      'shpjs$': 'shpjs/dist/shp.min.js',
      'a4maps_common$': 'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_common.js'
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
