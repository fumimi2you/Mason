# coding:utf-8

import numpy as np
import cv2

import mason_tools as wsht

# デバッグのレベル
global debug_out_lv
debug_out_lv = 1

def MakeSegImage( imgSrc ):
    imgSeg = cv2.pyrMeanShiftFiltering(imgSrc, 4, 16, 0 )
    return cv2.medianBlur(imgSeg, 3)

def ReFineCont( cont_array_valid, cont_array_invalid, img_seg, thick ) :
    """
    Refine the contour

    Parameters
    ----------
    cont : cv::Contour
        contour
    thick : float
        Refine strength

    Returns
    -------
    cont : cv::Contour
        refined contour
    """
    img = np.zeros((img_seg.shape[0], img_seg.shape[1], 1), np.uint8)

    # 有効領域の塗りつぶし
    cv2.drawContours( img, cont_array_valid, -1, (255, 255, 255 ), -1 )

    # 無効領域の削減
    # cv2.drawContours( img, cont_array_invalid, -1, (0, 0, 0 ), thick )
    cv2.drawContours( img, cont_array_invalid, -1, (0, 0, 0 ), -1 )

    # オープニングでノイズを殺す
    kernel = np.ones((3,3),np.uint8)
    img = cv2.erode(img, kernel, thick)
    img = cv2.dilate(img, kernel, thick)
    img_cnt, conts, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if debug_out_lv >= 2 :
        img_cnt_col = cv2.cvtColor(img_cnt, cv2.COLOR_GRAY2RGB)
        cv2.imshow("img_cnt_col", cv2.addWeighted( img_cnt_col, 0.5, img_seg, 0.5, 0 ) )
        # cv2.waitKey(0)

    return conts


def FindContFromSeedCore2(imgSrc, cont_init):
    
    imgInitCont = np.zeros((imgSrc.shape[0], imgSrc.shape[1], 1), np.uint8)
    imgRetMask = np.zeros((imgSrc.shape[0], imgSrc.shape[1], 1), np.uint8)

    cv2.drawContours( imgInitCont, [cont_init], -1, (255, 255, 255 ), -1 )
    
    kernel = np.ones((3,3),np.uint8)
    imgInitCont = cv2.dilate(imgInitCont, kernel, 3)
    pixInit = cv2.countNonZero(imgInitCont)

    sigma = 1.0
    k = 300
    minPix = int(imgSrc.shape[0]*imgSrc.shape[1]/100)
    segmentator = cv2.ximgproc.segmentation.createGraphSegmentation(sigma=sigma, k=k, min_size=minPix)
    segment = segmentator.processImage(imgSrc)
    mask = segment.reshape(list(segment.shape) + [1]).repeat(3, axis=2)
    masked = np.ma.masked_array(imgSrc, fill_value=0)
    for i in range(np.max(segment)):
        masked.mask = mask != i
        imgMasked = masked.filled().copy()
        # 二値変換
        _, imgMaskedG = cv2.threshold(cv2.cvtColor(imgMasked, cv2.COLOR_BGR2GRAY),
                                    1, 255, cv2.THRESH_BINARY)
        
        pixMasked = cv2.countNonZero(imgMaskedG)
        pixValid = cv2.countNonZero( cv2.bitwise_and( imgMaskedG, imgInitCont ) )

        if pixValid > ( pixMasked * 0.25 ) or pixValid > (pixInit * 0.5) :
            imgRetMask = cv2.bitwise_or( imgMaskedG, imgRetMask ) 

        # cv2.imshow('masked_{num}'.format(num=i), imgMaskedG)

        #y, x = np.where(segment == i)
        #top, bottom, left, right = min(y), max(y), min(x), max(x)
        #dst = masked.filled()[top : bottom + 1, left : right + 1]   
        #cv2.imshow('segment_{num}'.format(num=i), dst)

    cv2.imshow("imgInitCont", imgInitCont)
    cv2.imshow("imgRetMask", imgRetMask)
    # cv2.imshow("imgRet", cv2.bitwise_and( imgSrc,imgRetMask))

    cv2.waitKey(1)

    _, cont_ret, _ = cv2.findContours(imgRetMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # 検出できていない場合の対処
    if len(cont_ret) == 0:
        _, cont_ret, _ = cv2.findContours(cv2.cvtColor(imgSrc, cv2.COLOR_BGR2GRAY), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


    return cont_ret[0]

def FindContFromSeed(imgSrc, cnt_src) :

    if len(cnt_src) <= 1 : 
        return None

    cont_list = list()
    for xy in cnt_src :
        cont_list.append( [int(xy["x"]), int(xy["y"])] )
    pts_init = np.array(cont_list, np.int32)

    # 処理領域
    img_h = imgSrc.shape[0]
    img_w = imgSrc.shape[1]
    rect_init = cv2.boundingRect(pts_init)
    rect_proc = [0,0,img_w,img_h]
    pixBuff = (img_w+img_h)/64
    rect_proc[0] = max( int(rect_init[0] - rect_init[2] * 0.5 - pixBuff), 0 )
    rect_proc[1] = max( int(rect_init[1] - rect_init[3] * 0.5 - pixBuff), 0 )
    rect_proc[2] = min( int(rect_init[2] * 2 + pixBuff * 2), img_w - rect_proc[0] )
    rect_proc[3] = min( int(rect_init[3] * 2 + pixBuff * 2), img_h - rect_proc[1] )
    #print(rect_proc)

    for xy in pts_init :
        xy[0] -= rect_proc[0]
        xy[1] -= rect_proc[1]


    # 初期輪郭を整形する
    cont_init = pts_init

    # 画像の切り出し
    img_trm = imgSrc[rect_proc[1]:rect_proc[1]+rect_proc[3],rect_proc[0]:rect_proc[0]+rect_proc[2]]

    if debug_out_lv >= 2 :
        cv2.imshow("img_trm", img_trm)

    # 輪郭検出
    cont_ret = FindContFromSeedCore2(img_trm, cont_init)
    # cont_ret = FindContFromSeedCore(img_trm, cont_init)

    for i in range( len(cont_ret) ):
        cont_ret[i][0][0] += rect_proc[0]
        cont_ret[i][0][1] += rect_proc[1]

    # cv2.waitKey(0)

    return cont_ret

