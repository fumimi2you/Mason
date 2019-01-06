
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
  console.log(req.query.id)
  var dat = req.query.pointList[0]
  console.log(JSON.parse(dat))
  var item = req.query.itemList[0]
  console.log(JSON.parse(item))
  // ここからdraw.jsを呼び出す
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