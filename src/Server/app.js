
const express = require('express')
const app = express()
const multer = require('multer')
const path = require('path')
const exec = require('child_process').exec
const fs = require('fs')

// uploadディレクトリを、絶対値表記にする  
const upDir = path.join(__dirname, 'upload'); 
const uploadDir = multer({dest: upDir}); 

app.listen(50000, () => console.log('Listening on port 50000'));
app.use(function (req, res, next) {
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE')
  res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type')
  res.setHeader('Access-Control-Allow-Credentials', true)
  next();
});

app.get('/api/v1/mason', (req, res) => {
  let x = Number(req.query.x)
  let y = Number(req.query.y)
  let json = {
    'imagePath':__dirname + '/upload/' + req.query.filename,
    "initialContours":[[
      { "x":x+10, "y":y+10 },
      { "x":x+10, "y":y-10 },
      { "x":x-10, "y":y+10 },
      { "x":x-10, "y":y-10 }
    ]]
  }
  fs.writeFileSync(__dirname + '/upload/' + req.query.filename + '.json', JSON.stringify(json));
      exec('python ../Python/Mason/Mason.py ' + __dirname + '/upload/' + req.query.filename + '.json', (err, stdout, stderr) => {
      if (err) { console.log(err); }
      res.json(JSON.parse(stdout))
    })
})

app.get('/process', (req, res) => {
  console.log(req.query.title)
  let dynamo = require('./dynamo.js')
  dynamo.setData(req.query,function(err,data){
    if (err) {
      console.log(err);
    } else {
      console.log(data);
    }
  })
  let draw = require('./draw.js')
  draw.save(req.query.id , req.query)
  res.json({"res":"OK"})
})

app.get('/cards', (req, res) => {
  let dynamo = require('./dynamo.js')
  dynamo.getData(function(err,data){
    console.log(data.Items)
    res.json(data.Items)
  })
})

app.post('/upload', uploadDir.single('upFile'), (req, res) => {
  var sizeOf = require('image-size')
  sizeOf(__dirname + '/upload/' + req.file.filename, function (err, dimensions) {
    res.json({
      'url':'http://localhost:50000/upload/' + req.file.filename,
      'filename':req.file.filename,
      'width':dimensions.width,
      'height':dimensions.height
    })
  })
})
app.use(express.static('public'));
app.use(express.static('upload'));

let cards = [
  {
    'url': 'b36fd20037011de57fd1779a5dfffc53',
    'like': 12,
    'level': '6級',
    'shop': 'shop name',
    'date': '2018/4/2',
    'auther': 'setter',
    'title': '虫歯',
    'detail': '手が痛くなる課題です。'
  },
  {
    'url': 'b36fd20037011de57fd1779a5dfffc53',
    'like': 12,
    'level': '3級',
    'shop': 'shop name',
    'date': '2018/4/2',
    'auther': 'setter',
    'title': 'マンスリー',
    'detail': '横移動をして行く課題です。足がフリーなので、ホールドの向きに合わせて体を移動させると良いです。'
  },
  {
    'url': 'b36fd20037011de57fd1779a5dfffc53',
    'like': 12,
    'level': '8級',
    'shop': 'shop name',
    'date': '2018/4/2',
    'auther': 'setter',
    'title': 'クアッド餓鬼',
    'detail': 'ヒールフックを使いましょう。'
  },
  {
    'url': 'b36fd20037011de57fd1779a5dfffc53',
    'like': 12,
    'level': '1級',
    'shop': 'xxxx',
    'date': '2018/4/2',
    'auther': 'xxx',
    'title': 'xxxx',
    'detail': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
  }
]