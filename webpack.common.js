const webpack = require('webpack')
const path = require('path')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  entry: {
    adhocracy4: [
      './adhocracy-plus/assets/scss/style.scss',
      './adhocracy-plus/assets/extra_css/_slick-theme.css',
      './adhocracy-plus/assets/js/app.js'
    ],
    platform: [
      './adhocracy-plus/assets/scss/platform.scss'
    ],
    common_unincluded: [
      'classnames',
      'immutability-helper',
      'js-cookie',
      'react',
      'react-dom',
      'react-flip-move',
      'slick-carousel/slick/slick.min.js',
      'typeface-libre-franklin',
      '@fortawesome/fontawesome-free/scss/fontawesome.scss',
      '@fortawesome/fontawesome-free/scss/brands.scss',
      '@fortawesome/fontawesome-free/scss/regular.scss',
      '@fortawesome/fontawesome-free/scss/solid.scss',
      'datepicker/css/datepicker.min.css',
      'leaflet/dist/leaflet.css',
      'leaflet-draw/dist/leaflet.draw.css',
      'leaflet.markercluster/dist/MarkerCluster.css',
      'mapbox-gl/dist/mapbox-gl.css',
      'slick-carousel/slick/slick.css'
    ],
    a4maps_display_point: [
      'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_display_point.js'
    ],
    a4maps_display_points: [
      'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_display_points.js'
    ],
    a4maps_choose_point: [
      'leaflet/dist/leaflet.css',
      'mapbox-gl/dist/mapbox-gl.css',
      'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_choose_point.js'
    ],
    a4maps_choose_polygon: [
      './apps/maps/assets/map_choose_polygon_with_preset.js'
    ],
    datepicker: [
      './adhocracy-plus/assets/js/init-picker.js'
    ],
    embed: [
      './adhocracy-plus/assets/js/embed.js'
    ],
    'popup-close': [
      './adhocracy-plus/assets/js/popup-close.js'
    ],
    unload_warning: [
      './apps/contrib/static/js/unload_warning.js'
    ],
    imageUploader: [
      'adhocracy4/adhocracy4/images/static/a4images/imageUploader.js'
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
      jquery$: 'jquery/dist/jquery.min.js',
      shpjs$: 'shpjs/dist/shp.min.js',
      a4maps_common$: 'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_common.js'
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
    new MiniCssExtractPlugin({
      filename: '[name].css',
      chunkFilename: '[name].css'
    }),
    new CopyWebpackPlugin([
      {
        from: './adhocracy-plus/assets/images/**/*',
        to: 'images/',
        flatten: true
      }
    ])
  ],
  optimization: {
    splitChunks: {
      cacheGroups: {
        leaflet: {
          test: /[\\/]node_modules[\\/](leaflet|leaflet-draw|leaflet.markercluster|mapbox-gl|mapbox-gl-leaflet)[\\/]/,
          name: 'leaflet',
          chunks: 'all',
          priority: 0
        },
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendor',
          chunks: 'all',
          priority: -100,
          reuseExistingChunk: true
        }
      }
    }
  }
}
