// Node.js標準装備のファイルの読み書きするやつ
var fs = require('fs');

// 別途用意した画像を保存してくれるやつ
var canvas_saver = require('./save.js');

// テスト用データ
var dada = [[ { y: 208, x: 445 },
    { y: 218, x: 435 },
    { y: 219, x: 435 },
    { y: 225, x: 429 },
    { y: 226, x: 429 },
    { y: 227, x: 428 },
    { y: 229, x: 428 },
    { y: 230, x: 427 },
    { y: 232, x: 427 },
    { y: 233, x: 426 },
    { y: 241, x: 426 },
    { y: 242, x: 427 },
    { y: 243, x: 427 },
    { y: 244, x: 428 },
    { y: 246, x: 428 },
    { y: 247, x: 429 },
    { y: 250, x: 429 },
    { y: 251, x: 430 },
    { y: 252, x: 430 },
    { y: 255, x: 433 },
    { y: 255, x: 434 },
    { y: 249, x: 440 },
    { y: 247, x: 440 },
    { y: 246, x: 441 },
    { y: 241, x: 441 },
    { y: 240, x: 442 },
    { y: 237, x: 442 },
    { y: 236, x: 443 },
    { y: 234, x: 443 },
    { y: 233, x: 444 },
    { y: 231, x: 444 },
    { y: 230, x: 445 },
    { y: 228, x: 445 },
    { y: 227, x: 446 },
    { y: 226, x: 446 },
    { y: 225, x: 447 },
    { y: 224, x: 447 },
    { y: 223, x: 448 },
    { y: 221, x: 448 },
    { y: 219, x: 450 },
    { y: 218, x: 450 },
    { y: 217, x: 451 },
    { y: 216, x: 451 },
    { y: 214, x: 453 },
    { y: 212, x: 453 },
    { y: 209, x: 450 },
    { y: 209, x: 449 },
    { y: 208, x: 448 } ],
    [{ y: 139, x: 511 },
        { y: 140, x: 510 },
        { y: 140, x: 509 },
        { y: 141, x: 508 },
        { y: 141, x: 507 },
        { y: 150, x: 498 },
        { y: 151, x: 498 },
        { y: 152, x: 497 },
        { y: 153, x: 497 },
        { y: 154, x: 496 },
        { y: 157, x: 496 },
        { y: 158, x: 495 },
        { y: 161, x: 495 },
        { y: 162, x: 496 },
        { y: 165, x: 496 },
        { y: 166, x: 497 },
        { y: 167, x: 497 },
        { y: 168, x: 498 },
        { y: 169, x: 498 },
        { y: 177, x: 506 },
        { y: 177, x: 507 },
        { y: 178, x: 508 },
        { y: 178, x: 509 },
        { y: 179, x: 510 },
        { y: 179, x: 518 },
        { y: 177, x: 520 },
        { y: 177, x: 521 },
        { y: 169, x: 529 },
        { y: 168, x: 529 },
        { y: 166, x: 531 },
        { y: 165, x: 531 },
        { y: 164, x: 532 },
        { y: 162, x: 532 },
        { y: 161, x: 533 },
        { y: 152, x: 533 },
        { y: 151, x: 532 },
        { y: 150, x: 532 },
        { y: 149, x: 531 },
        { y: 148, x: 531 },
        { y: 141, x: 524 },
        { y: 141, x: 523 },
        { y: 140, x: 522 },
        { y: 140, x: 520 },
        { y: 139, x: 519 } ],
        [{ y: 139, x: 511 },
            { y: 140, x: 510 },
            { y: 140, x: 509 },
            { y: 141, x: 508 },
            { y: 141, x: 507 },
            { y: 150, x: 498 },
            { y: 151, x: 498 },
            { y: 152, x: 497 },
            { y: 153, x: 497 },
            { y: 154, x: 496 },
            { y: 157, x: 496 },
            { y: 158, x: 495 },
            { y: 161, x: 495 },
            { y: 162, x: 496 },
            { y: 165, x: 496 },
            { y: 166, x: 497 },
            { y: 167, x: 497 },
            { y: 168, x: 498 },
            { y: 169, x: 498 },
            { y: 177, x: 506 },
            { y: 177, x: 507 },
            { y: 178, x: 508 },
            { y: 178, x: 509 },
            { y: 179, x: 510 },
            { y: 179, x: 518 },
            { y: 177, x: 520 },
            { y: 177, x: 521 },
            { y: 169, x: 529 },
            { y: 168, x: 529 },
            { y: 166, x: 531 },
            { y: 165, x: 531 },
            { y: 164, x: 532 },
            { y: 162, x: 532 },
            { y: 161, x: 533 },
            { y: 152, x: 533 },
            { y: 151, x: 532 },
            { y: 150, x: 532 },
            { y: 149, x: 531 },
            { y: 148, x: 531 },
            { y: 141, x: 524 },
            { y: 141, x: 523 },
            { y: 140, x: 522 },
            { y: 140, x: 520 },
            { y: 139, x: 519 } ],
          [ { y: 280, x: 466 },
            { y: 283, x: 463 },
            { y: 285, x: 463 },
            { y: 290, x: 458 },
            { y: 301, x: 458 },
            { y: 303, x: 456 },
            { y: 306, x: 456 },
            { y: 308, x: 458 },
            { y: 310, x: 458 },
            { y: 314, x: 462 },
            { y: 314, x: 465 },
            { y: 310, x: 469 },
            { y: 308, x: 469 },
            { y: 307, x: 470 },
            { y: 306, x: 470 },
            { y: 305, x: 471 },
            { y: 305, x: 478 },
            { y: 302, x: 481 },
            { y: 298, x: 481 },
            { y: 297, x: 480 },
            { y: 296, x: 480 },
            { y: 295, x: 479 },
            { y: 291, x: 479 },
            { y: 284, x: 472 },
            { y: 283, x: 472 },
            { y: 280, x: 469 } ],
            [{ y: 47, x: 594 },
                { y: 48, x: 593 },
                { y: 48, x: 592 },
                { y: 54, x: 586 },
                { y: 54, x: 584 },
                { y: 60, x: 578 },
                { y: 61, x: 578 },
                { y: 62, x: 577 },
                { y: 63, x: 577 },
                { y: 64, x: 576 },
                { y: 67, x: 576 },
                { y: 68, x: 577 },
                { y: 72, x: 577 },
                { y: 73, x: 578 },
                { y: 78, x: 578 },
                { y: 83, x: 583 },
                { y: 83, x: 584 },
                { y: 85, x: 586 },
                { y: 85, x: 590 },
                { y: 84, x: 591 },
                { y: 84, x: 593 },
                { y: 80, x: 597 },
                { y: 80, x: 600 },
                { y: 73, x: 607 },
                { y: 72, x: 607 },
                { y: 71, x: 608 },
                { y: 66, x: 608 },
                { y: 65, x: 607 },
                { y: 64, x: 607 },
                { y: 63, x: 606 },
                { y: 62, x: 606 },
                { y: 61, x: 605 },
                { y: 57, x: 605 },
                { y: 56, x: 604 },
                { y: 52, x: 604 },
                { y: 48, x: 600 },
                { y: 48, x: 599 },
                { y: 47, x: 598 }],
                [{ y: 389, x: 535 },
                    { y: 390, x: 534 },
                    { y: 390, x: 533 },
                    { y: 391, x: 532 },
                    { y: 391, x: 531 },
                    { y: 393, x: 529 },
                    { y: 396, x: 529 },
                    { y: 398, x: 531 },
                    { y: 399, x: 531 },
                    { y: 403, x: 535 },
                    { y: 403, x: 537 },
                    { y: 401, x: 539 },
                    { y: 399, x: 539 },
                    { y: 398, x: 540 },
                    { y: 395, x: 540 },
                    { y: 394, x: 541 },
                    { y: 393, x: 541 },
                    { y: 392, x: 540 },
                    { y: 391, x: 540 },
                    { y: 389, x: 538 } ]
];

var itit = [{ item: 'start', x: 422.03333333333336, y: 237.53846153846155 },{ item: 'top', x: 541.6666666666666, y: 77.53846153846155 }];

let drawPoints = function (ctx, pointList) {
    for(var j = 0; j < pointList.length;j ++){
        let datum = pointList[j];
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
    var data = fs.readFileSync(__dirname + filename)
    let img = new Image;
    img.src = data;
    return img;
}

let test = function (filename,pointList) {
    // node-canvas
    var Canvas = require('canvas'),
    Image = Canvas.Image;
    var baseImg = getImage(filename,Image);

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

    for(var jj = 0 ; jj < itit.length; jj ++) {
        let item = itit[jj];
        let imgName = '';
        if(item.item === 'start') {
            imgName = '/assets/start.svg'
        }
        else if(item.item === 'top') {
            imgName = '/assets/top.svg'
        }
        let itemImg = getImage(imgName,Image);
        ctx.drawImage(itemImg,item.x,item.y);
    }

    var logoImg = getImage('/assets/logo.png',Image);

    ctx.drawImage(logoImg,baseImg.width - (logoImg.width/3),baseImg.height-(logoImg.height/3),logoImg.width/3,logoImg.height/3);
    // データを保存
    canvas_saver.save(canvas, "monochrome.png", function(){
        console.log("画像保存完了したよ!!");
    });
}

test('/indata.png',dada);