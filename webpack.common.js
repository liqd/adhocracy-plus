const webpack = require('webpack')
const path = require('path')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  entry: {
    adhocracy4: [
      'slick-carousel/slick/slick.css',
      './adhocracy-plus/assets/extra_css/_slick-theme.css',
      './adhocracy-plus/assets/scss/style.scss',
      './adhocracy-plus/assets/js/app.js'
    ],
    platform: [
      './adhocracy-plus/assets/scss/platform.scss'
    ],
    vendor: [
      '@fortawesome/fontawesome-free/scss/fontawesome.scss',
      '@fortawesome/fontawesome-free/scss/brands.scss',
      '@fortawesome/fontawesome-free/scss/regular.scss',
      '@fortawesome/fontawesome-free/scss/solid.scss',
      'classnames',
      'immutability-helper',
      'js-cookie',
      'react',
      'react-dom',
      'react-flip-move',
      'typeface-libre-franklin'
    ],
    datepicker: [
      './adhocracy-plus/assets/js/init-picker.js',
      'datepicker/css/datepicker.min.css'
    ],
    embed: [
      'bootstrap/js/dist/modal.js',
      './apps/embed/assets/embed.js'
    ],
    // A4 dependencies - we want all of them to go through webpack
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
      // overwrite the A4 version
      './apps/maps/assets/map_choose_polygon_with_preset.js'
    ],
    category_formset: [
      'adhocracy4/adhocracy4/categories/assets/category_formset.js'
    ],
    image_uploader: [
      'adhocracy4/adhocracy4/images/assets/image_uploader.js'
    ],
    select_dropdown_init: [
      'adhocracy4/adhocracy4/categories/assets/select_dropdown_init.js'
    ]
  },
  output: {
    libraryTarget: 'this',
    library: '[name]',
    path: path.resolve('./adhocracy-plus/static/'),
    publicPath: '/static/',
    filename: '[name].js'
  },
  externals: {
    django: 'django'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules\/(?!(adhocracy4)\/).*/, // exclude all dependencies but adhocracy4
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
              plugins: [
                require('autoprefixer')
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
      a4maps_common$: 'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_common.js',
      bootstrap$: 'bootstrap/dist/js/bootstrap.bundle.min.js',
      'file-saver': 'file-saver/dist/FileSaver.min.js',
      jquery$: 'jquery/dist/jquery.min.js',
      shpjs$: 'shpjs/dist/shp.min.js',
      tether$: 'tether/dist/js/tether.min.js',
      'slick-carousel$': 'slick-carousel/slick/slick.min.js'
    },
    // when using `npm link`, dependencies are resolved against the linked
    // folder by default. This may result in dependencies being included twice.
    // Setting `resolve.root` forces webpack to resolve all dependencies
    // against the local directory.
    modules: [path.resolve('./node_modules')]
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      'window.$': 'jquery',
      'window.jQuery': 'jquery',
      tether: 'tether',
      Tether: 'tether',
      'window.Tether': 'tether',
      timeago: 'timeago.js'
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
        from: './adhocracy-plus/assets/images/**/*',
        to: 'images/',
        flatten: true
      }
    ])
  ]
}
