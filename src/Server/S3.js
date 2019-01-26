module.exports = (function(){
  var AWS = require('aws-sdk');

  AWS.config.loadFromPath('./rootkey.json');
  AWS.config.update({region: 'ap-northeast-1'});

  let upload = function (image,filename) {
    var s3 = new AWS.S3();
    var params = {
      Bucket: "bl-images",
      Key: filename
    };
    //var v= fs.readFileSync(__dirname + '/upload/' + filenmae);
    params.Body=image;
    s3.putObject(params, function(err, data) {
      if (err) console.log(err, err.stack);
      else     console.log(data);
    });
  }

  return {
    save: function(image,filename){
      upload(image,filename)
    }
  }
})();