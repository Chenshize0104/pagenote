const path = require('path');
const merge = require('webpack-merge');
const common = require('./webpack.common.js');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = merge(common, {
  entry: './dev/index.js',
  mode:"development",
  devtool: 'inline-source-map',
  output: {
    path: path.resolve(__dirname, 'public'),
    filename: 'pagenote.js',
    libraryTarget: 'umd'
  },
  devServer: {
    contentBase: './public',
    hot: true
  },
  plugins:[
    new webpack.HotModuleReplacementPlugin(),
    new HtmlWebpackPlugin({
      inject: false,
      templateContent: ({htmlWebpackPlugin}) => `
    <html>
      <head>
        <link href="https://pagenote.cn/favicon.ico" rel="shortcut icon">
        ${htmlWebpackPlugin.tags.headTags}
        <title>pagenote 开发页</title>
        <meta name="description" content="这是pagenote 开发页面" />
        <meta name="keywords" content="keywords, 标记" />
        <style>
          .scroll{
            margin-top: 100px;
            position: relative;
            height: 80vh;
            overflow: scroll;
          }
        </style>
      </head>
      <body data-blockpagenote='1'>
        <div id="guide" data-blockpagenote="1"></div>
        ${htmlWebpackPlugin.tags.bodyTags}
      </body>
    </html>
  `
    })
  ]
});