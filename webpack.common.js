const webpack = require('webpack')
const path = require('path')
const glob = require('glob')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = {
  entry: {
    adhocracy4: {
      import: [ // array of entry points
        '@fortawesome/fontawesome-free/scss/fontawesome.scss',
        '@fortawesome/fontawesome-free/scss/brands.scss',
        '@fortawesome/fontawesome-free/scss/regular.scss',
        '@fortawesome/fontawesome-free/scss/solid.scss',
        'select2/dist/css/select2.min.css',
        'slick-carousel/slick/slick.css',
        './adhocracy-plus/assets/extra_css/_slick-theme.css',
        './adhocracy-plus/assets/scss/style.scss',
        './adhocracy-plus/assets/js/app.js'
      ],
      // exposes a4 in this / window
      library: {
        name: '[name]',
        type: 'this'
      }
    },
    captcheck: {
      import: [
        './apps/captcha/assets/captcheck.js'
      ],
      // shares dependency so not loaded repeatedly
      dependOn: 'adhocracy4'
    },
    datepicker: {
      import: [
        './adhocracy-plus/assets/js/init-picker.js',
        'datepicker/css/datepicker.min.css'
      ],
      dependOn: 'adhocracy4'
    },
    documents: {
      import: [
        './apps/documents/assets/react_documents_init.jsx'
      ]
    },
    dsgvo_video_embed: {
      import: [
        'dsgvo-video-embed/dist/dsgvo-video-embed.min.css',
        'dsgvo-video-embed/dist/dsgvo-video-embed.min.js'
      ],
      dependOn: 'adhocracy4'
    },
    interactiveevents: {
      import: [
        './apps/interactiveevents/assets/react_interactiveevents_init.jsx'
      ]
    },
    interactiveevents_presents: {
      import: [
        './apps/interactiveevents/assets/react_interactiveevents_present_init.jsx'
      ]
    },
    init_dashboard_accordion: {
      import: [
        './adhocracy-plus/assets/js/init_dashboard_accordion.js'
      ]
    },
    moderation_projects: {
      import: [
        './apps/userdashboard/assets/js/a4_candy_userdashboard/react_moderation_projects.jsx'
      ]
    },
    moderation_notification_list: {
      import: [
        './apps/userdashboard/assets/js/a4_candy_userdashboard/react_moderation_notification_list.jsx'
      ]
    },
    unload_warning: {
      import: [
        './adhocracy-plus/assets/js/unload_warning.js'
      ],
      dependOn: 'adhocracy4'
    },
    // A4 dependencies - we want all of them to go through webpack
    a4maps_display_point: {
      import: [
        'leaflet/dist/leaflet.css',
        'maplibre-gl/dist/maplibre-gl.css',
        'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_display_point.js'
      ],
      dependOn: 'adhocracy4'
    },
    a4maps_display_points: {
      import: [
        'leaflet/dist/leaflet.css',
        'maplibre-gl/dist/maplibre-gl.css',
        'leaflet.markercluster/dist/MarkerCluster.css',
        'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_display_points.js'
      ],
      dependOn: 'adhocracy4'
    },
    a4maps_choose_point: {
      import: [
        'leaflet/dist/leaflet.css',
        'maplibre-gl/dist/maplibre-gl.css',
        'adhocracy4/adhocracy4/maps/static/a4maps/a4maps_choose_point.js'
      ],
      dependOn: 'adhocracy4'
    },
    a4maps_choose_polygon: {
      import: [
        'leaflet/dist/leaflet.css',
        'maplibre-gl/dist/maplibre-gl.css',
        'leaflet-draw/dist/leaflet.draw.css',
        // overwrite the A4 version
        './apps/maps/assets/map_choose_polygon_with_preset.js'
      ],
      dependOn: 'adhocracy4'
    },
    category_formset: {
      import: [
        'adhocracy4/adhocracy4/categories/assets/category_formset.js'
      ],
      dependOn: 'adhocracy4'
    },
    image_uploader: {
      import: [
        'adhocracy4/adhocracy4/images/assets/image_uploader.js'
      ],
      dependOn: 'adhocracy4'
    },
    poll_management: {
      import: [
        'adhocracy4/adhocracy4/polls/static/react_poll_management.jsx'
      ],
      dependOn: 'adhocracy4'
    },
    polls: {
      import: [
        'adhocracy4/adhocracy4/polls/static/react_polls.jsx'
      ],
      dependOn: 'adhocracy4'
    },
    select_dropdown_init: {
      import: [
        'adhocracy4/adhocracy4/categories/assets/select_dropdown_init.js'
      ],
      dependOn: 'adhocracy4'
    }
  },
  output: {
    // creates a folder to store all assets
    path: path.resolve('./adhocracy-plus/static/'),
    // location they can be accessed, can also be a url
    publicPath: '/static/'
  },
  externals: {
    django: 'django'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules\/(?!(adhocracy4)\/).*/, // exclude all dependencies but adhocracy4
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'].map(require.resolve),
            plugins: ['@babel/plugin-transform-runtime', '@babel/plugin-transform-modules-commonjs']
          }
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
              postcssOptions: {
                plugins: [
                  require('autoprefixer')
                ]
              }
            }
          },
          {
            loader: 'sass-loader'
          }
        ]
      },
      {
        test: /(fonts|files)\/.*\.(svg|woff2?|ttf|eot|otf)(\?.*)?$/,
        // defines asset should always have seperate file
        type: 'asset/resource',
        generator: {
          // defines custom location of those files
          filename: 'fonts/[name][ext]'
        }
      },
      {
        test: /\.svg$|\.png$/,
        type: 'asset/resource',
        generator: {
          filename: 'images/[name][ext]'
        }
      }
    ]
  },
  resolve: {
    // redirect module requests when normal resolving fails.
    fallback: {
      path: require.resolve('path-browserify')
    },
    // attempt to resolve these extensions in this order.
    extensions: ['*', '.js', '.jsx', '.scss', '.css'],
    // create aliases to import or require certain modules more easily, $ signifys exact match
    alias: {
      bootstrap$: 'bootstrap/dist/js/bootstrap.bundle.min.js',
      'file-saver': 'file-saver/dist/FileSaver.min.js',
      jquery$: 'jquery/dist/jquery.min.js',
      shpjs$: 'shpjs/dist/shp.min.js',
      'slick-carousel$': 'slick-carousel/slick/slick.min.js'
    },
    // when using `npm link` for a4 dev env, dependencies are resolved against the linked
    // folder by default. This may result in dependencies being included twice.
    // Resolving against node_modules will prevent this.
    // concat merges node_modules and assets and syncs both to ensure no duplication.
    modules: [
      path.resolve('./node_modules')
    ].concat(
      glob.sync('./apps/*/assets/js').map(e => { return path.resolve(e) })
    )
  },
  plugins: [
    // automatically load modules instead of import or require them everywhere.
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery',
      'window.$': 'jquery',
      'window.jQuery': 'jquery',
      timeago: 'timeago.js'
    }),
    // extracts CSS into separate files
    new MiniCssExtractPlugin({
      filename: '[name].css',
      chunkFilename: '[id].css'
    }),
    // copies files or directories, to the build directory.
    new CopyWebpackPlugin({
      patterns: [{
        from: './adhocracy-plus/assets/images/**/*',
        to: 'images/[name][ext]'
      }]
    })
  ]
}
