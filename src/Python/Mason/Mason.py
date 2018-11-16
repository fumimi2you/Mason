import sys
import os
import time
import json 

# OpenCv インストールしてけろ。
import numpy as np
import cv2


# デバッグのレベル
global debug_out_lv
debug_out_lv = 0

def ArcRatio(cont) :
    """
    concentration of contour

    Parameters
    ----------
    cont : cv::Contour
        contour

    Returns
    -------
    ret : float
        concentration
        circle = π/4 (≒0.785)
        square = 1
        rect(1:2)= 1.125
    """
    arcLen = float( cv2.arcLength(cont, True) )
    area = float( cv2.contourArea(cont) )
    if area <= 1:
        return 9999.9
    else :
        ret = (arcLen / 4) * (arcLen / 4) / area
        return ret

def ReFineCont( cont, thick ) :
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
    rect = cv2.boundingRect(cont)
    img = np.zeros((rect[1]+rect[3]+(thick*4), rect[0]+rect[2]+(thick*4), 1), np.uint8)
    cv2.polylines( img, [cont], True, 255, thick )
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((thick,thick),np.uint8))
    img, conts, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if debug_out_lv >= 2 :
        cv2.imshow("cont", img )

    return conts[0]

def FindContRet(img_seg, cont_init, ratio_min, cth) :
    """
    Detect contour candidate

    Parameters
    ----------
    img_seg : cv::Mat
        input image.
    cont_init : cv::Contour
        Initial contour
    ratio_min :  float
        Minimum evaluation value
    cth : float
        threshold of canny

    Returns
    -------
    ratio_min : float
        The detected minimum evaluation value
    cont_ret : cv::Contour
        The detected Contour
    """

    # 評価対象の輪郭
    rect_init = cv2.boundingRect(cont_init)
    area_init = cv2.contourArea(cont_init) * 1.2 # 小さめにマークされる事が多いため、少し大きくする
    ptc_x = rect_init[0] + rect_init[2]/2
    ptc_y = rect_init[1] + rect_init[3]/2

    # グレイ変換してキャニー
    img_gry = cv2.cvtColor(img_seg, cv2.COLOR_BGR2GRAY)
    img_cny = cv2.Canny(img_gry, cth, cth*1.5)

    # クロージングして輪郭検出
    cont_ret = []
    for mth in range(2, 5, 2):

        img_cls = cv2.morphologyEx(img_cny, cv2.MORPH_CLOSE, np.ones((mth,mth),np.uint8))
        _, contours, _ = cv2.findContours(img_cls, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if debug_out_lv >= 3:
            cv2.imshow("img_cls_" + str(int(cth)) + "_" + str(mth) , img_cls)

        for cont in contours:
            area_cnt = float( cv2.contourArea(cont) )
            aratio = float( ArcRatio(cont))
            if area_cnt > 1 and aratio < 16 and cv2.pointPolygonTest(cont,(ptc_x,ptc_y),False) > 0 :
                ratio = ( max(area_init, area_cnt) / min(area_init, area_cnt) ) * aratio
                #print(match_val)
                if ratio < ratio_min:
                    print( "cth, mth, ratio : " + str(cth) + ", " + str(mth) + ", " + str(ratio) )
                    cont_ret = cont
                    ratio_min = ratio
        
        if ratio_min <= 2 :
            break

    return ratio_min, cont_ret

############################################################################
## MainFunction
############################################################################

# print(sys.version_info)
start = time.time()

# jsonを読み込み
json_path = "C:\Projects\_study\Python\sample\\_tmp.json"
if len(sys.argv) >= 2:
    json_path = sys.argv[1]
    print( json_path )
if len(sys.argv) >= 3 :
    debug_out_lv = int(sys.argv[2])
    print( debug_out_lv )
file_json = open(json_path, 'r') 
json_dict = json.load(file_json) 
file_json.close()

# データの取り出しと整形
file_path = json_dict["imagePath"]
init_cnt_data = json_dict["initialContours"][0]
cont_list = list()
for xy in init_cnt_data :
    cont_list.append( [int(xy["x"]), int(xy["y"])] )
pts_init = np.array(cont_list, np.int32)

# 画像を読む
img_org = cv2.imread(file_path)
img_h = img_org.shape[0]
img_w = img_org.shape[1]

# 処理領域を決める
rect_init = cv2.boundingRect(pts_init)
rect_proc = [0,0,0,0]
rect_proc[0] = max( rect_init[0] - rect_init[2], 0 )
rect_proc[1] = max( rect_init[1] - rect_init[3], 0 )
rect_proc[2] = min( rect_init[2] * 3, img_w - rect_proc[0] )
rect_proc[3] = min( rect_init[3] * 3, img_h - rect_proc[1] )
print(rect_proc)

for xy in pts_init :
    xy[0] -= rect_proc[0]
    xy[1] -= rect_proc[1]


# 初期輪郭を整形する
cont_init = ReFineCont( pts_init, 2 )

# 画像の切り出しとセグメンテーション
img_trm = img_org[rect_proc[1]:rect_proc[1]+rect_proc[3],rect_proc[0]:rect_proc[0]+rect_proc[2]]
img_seg = cv2.pyrMeanShiftFiltering(img_trm, 4, 16, 0 )
img_seg = cv2.medianBlur(img_seg, 3)

if debug_out_lv >= 2 :
    cv2.imshow("img_seg", img_seg)


# 輪郭検出
ratio_min = 9999.0
cont_ret = cont_init
th = 128
while ratio_min >= 2 and th >= 16:
    ratio, cont_fnd = FindContRet(img_seg, cont_init, ratio_min, th )
    if ratio < ratio_min:
        ratio_min = ratio
        cont_ret = cont_fnd
    th /= 1.4

cont_ret = ReFineCont(cont_ret, 4)


# json出力
pts_ret = []
for i in range( len(cont_ret) ):
    x = cont_ret[i][0][0]
    y = cont_ret[i][0][1]
    pt_dic = {}
    pt_dic["x"] = int(x) + rect_proc[0]
    pt_dic["y"] = int(y) + rect_proc[1]
    pts_ret.append( pt_dic )

dict_ret = {}
dict_ret["contours"] = [pts_ret]

#print(json.dumps(dict_ret, indent=4))
root, ext = os.path.splitext(json_path)
output_path = root + "_Mason" + ext
f = open(output_path, "w")
json.dump(dict_ret,f,indent=4)
f.close()


elapsed_time = time.time() - start
print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")


# 画像のと表示
img_mask = np.zeros((rect_proc[3], rect_proc[2], 3), np.uint8)
img_mask = cv2.drawContours(img_mask, [cont_ret], 0, (255,255,255), -1)
img_mask = cv2.bitwise_and( img_seg.copy(), img_mask )

alpha = 0.75
img_ret = cv2.addWeighted(img_mask, alpha, img_seg, 1 - alpha, 0) 
img_ret = cv2.drawContours(img_ret, [cont_ret], 0, (255,255,255), 2)

cv2.imwrite(root + "_Mason.jpg", img_ret)
if debug_out_lv >= 1:
    cv2.imshow("img_ret", img_ret )
    cv2.waitKey(0)
    cv2.destroyAllWindows()
