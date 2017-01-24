var webpack = require('webpack');
var path = require('path');
var staticRoot = path.resolve(__dirname, '..');

module.exports = {
  entry: {
    app: "./app.js",
  },
  devtool: 'source-map',
  output: {
    path: __dirname,
    publicPath: "http://localhost:8080/assets/",
    filename: "build/[name].bundle.js",
  },
  resolve: {
    alias: {
      'scss': path.resolve(staticRoot, 'scss'),
    },
    extensions: ['', '.js', '.jsx'],
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        loaders: ['react-hot', 'babel', 'eslint'],
        exclude: /node_modules/,
      },
      {
        test: /\.scss$/,
        loaders: ['style', 'css', 'sass'],
        exclude: /node_modules/,
      }
    ],
  }
};
