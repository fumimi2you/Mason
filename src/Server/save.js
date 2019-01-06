// node-canvasのcanvasを画像データとして保存する

module.exports = (function(){
  "use strict";

  let fs = require('fs');

  let canvas_to_base64 = function(canvas){
      return canvas.toDataURL().split(',')[1];
  }

  // 追記: もっと簡単にできる方法がたしかあります(その方法は忘れました)
  let decode_and_copy = function(string, filename, callback) {
      let buffer = new Buffer(string, 'base64');
      fs.writeFile(filename, buffer, callback);
  }

  return {
      save: function(canvas, name, callback){
          decode_and_copy(
              canvas_to_base64(canvas),
              name,
              callback
          );
      }
  }

})();