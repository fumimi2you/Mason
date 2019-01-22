module.exports = (function(){
  var AWS = require('aws-sdk');

  var dynamodb = new AWS.DynamoDB({region: 'us-east-1'});
  var docClient = new AWS.DynamoDB.DocumentClient({region: 'us-east-1'});

  let fetch = function(callback) {
    let params = {TableName:'bl-card',Select: "ALL_ATTRIBUTES"};
    dynamodb.scan(params, callback);
  }

  let upload = function(data,callback) {
    let today=new Date(); 
    //年・月・日・曜日を取得する
    let year = today.getFullYear();
    let month = today.getMonth()+1;
    let day = today.getDate();

    let card = {
      date: year + '/' + month + '/' + day,
      detail: data.detail,
      shop: 'shop',
      level: data.level,
      auther: 'admin',
      like: 1,
      url: data.id,
      title: data.title
    };
    console.log(card)
    let params = {
      TableName: 'bl-card',
      Item: card
    };
    docClient.put(params,callback);
  }

  return {
    getData: function(callback){
      fetch(callback)
    },
    setData:  function(data,callback){
      upload(data,callback)
    }
  }
})();

/*
test(function(err,data){
  console.log(data);
})
*/