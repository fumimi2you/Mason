
module.exports = (function(){
    var fs = require('fs');
    var canvas_saver = require('./save.js');

    let drawPoints = function (ctx, pointList) {
        for(var j = 0; j < pointList.length;j ++){
            let datum = JSON.parse(pointList[j]);
            ctx.strokeStyle = 'rgba(84, 121 , 161 , 1.0)'
            ctx.lineWidth = 4;
            ctx.beginPath()
            ctx.moveTo( datum[0].x, datum[0].y );
            for(var i = 1; i < datum.length; i ++){
                var data = datum[i]
                ctx.lineTo( data.x, data.y );
            }
            ctx.closePath();
            ctx.stroke();

            ctx.strokeStyle = 'rgba(255, 255 , 255 , 1.0)'
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo( datum[0].x, datum[0].y );
            for(var i = 1; i < datum.length; i ++){
                var data = datum[i]
                ctx.lineTo( data.x, data.y );
            }
            ctx.closePath();
            ctx.stroke();
        }
    }

    let getImage = function (filename,Image) {
        console.log(filename)
        var data = fs.readFileSync(__dirname + filename)
        let img = new Image;
        img.src = data;
        return img;
    }

    let test = function (filename,data) {
        // node-canvas
        let pointList = data.pointList;
        let itemList = data.itemList;
        var Canvas = require('canvas'),
        Image = Canvas.Image;
        var baseImg = getImage('/upload/' + filename,Image);
        console.log(baseImg)

        var canvas = Canvas.createCanvas(baseImg.width, baseImg.height);
        var ctx = canvas.getContext('2d');
        ctx.drawImage(baseImg, 0, 0, baseImg.width, baseImg.height);

        // RGBの画素値の配列を取得
        var imagedata = ctx.getImageData(0, 0, baseImg.width, baseImg.height);

        // 画像加工(擬似モノクロ化)
        for(var y=0; y<imagedata.height; y++){
            for(var x=0; x<imagedata.width; x++){
                var index = (y*imagedata.width+x)*4;
                // imagedata.data[index] = imagedata.data[index]; // R
                imagedata.data[index+1] = imagedata.data[index]; // G
                imagedata.data[index+2] = imagedata.data[index]; // B
                // imagedata.data[index+3]; // alpha
            }
        }

        ctx.putImageData(imagedata, 0, 0);
        drawPoints(ctx,pointList);

        for(var jj = 0 ; jj < itemList.length; jj ++) {
            let item = JSON.parse(itemList[jj]);
            let imgName = '';
            if(item.item === 'start') {
                imgName = '/assets/start.svg'
            }
            else if(item.item === 'top') {
                imgName = '/assets/top.svg'
            }
            console.log(item)
            console.log(item.item)
            let itemImg = getImage(imgName,Image);
            ctx.drawImage(itemImg,item.x,item.y);
        }

        var logoImg = getImage('/assets/logo.png',Image);

        ctx.drawImage(logoImg,baseImg.width - (logoImg.width/3),baseImg.height-(logoImg.height/3),logoImg.width/3,logoImg.height/3);
        // データを保存
        canvas_saver.save(canvas, filename , function(){
            console.log("画像保存完了したよ!!");
        });
    }
    return {
        save: function(filename, data){
            test(filename,data);
        }
    }
})();
//test('/indata.png',dada);