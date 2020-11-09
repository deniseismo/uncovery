const path = require('path');
const HTMLPlugin = require('html-webpack-plugin');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.[chunkhash].js',
    path: path.resolve(__dirname, 'uncover/static')
  },
  devServer: {
    port: 3000
  },
  plugins: [
    new HTMLPlugin({
      template: "./src/layout.html"
    })
  ]
}