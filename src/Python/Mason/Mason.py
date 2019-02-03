# coding:utf-8
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
    cv2.drawContours( img, cont_array_invalid, 0, (0, 0, 0 ), -1 )

    # img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, np.ones((thick,thick),np.uint8))
    kernel = np.ones((3,3),np.uint8)
    img = cv2.dilate(img, kernel, thick)
    img = cv2.erode(img, kernel, thick)
    img_cnt, conts, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if debug_out_lv >= 2 :
        img_cnt_col = cv2.cvtColor(img_cnt, cv2.COLOR_GRAY2RGB)
        cv2.imshow("img_cnt_col", cv2.addWeighted( img_cnt_col, 0.5, img_seg, 0.5, 0 ) )

    return conts

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

    if debug_out_lv >= 2:
        img_cny_col = cv2.cvtColor(img_cny, cv2.COLOR_GRAY2RGB)
        cv2.imshow("img_cny", cv2.addWeighted( img_cny_col, 0.5, img_seg, 0.5, 0 ))

    # クロージングして輪郭検出
    cont_ret = []
    for mth in range(2, 5, 2):

        # img_cls = cv2.morphologyEx(img_cny, cv2.MORPH_CLOSE, np.ones((mth,mth),np.uint8))
        kernel = np.ones((3,3),np.uint8)
        img_dil = cv2.dilate(img_cny, kernel, mth)
        img_cls = cv2.erode(img_dil, kernel, mth)
        _, contours, _ = cv2.findContours(img_cls, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if debug_out_lv >= 3:
            img_cls_col = cv2.cvtColor(img_cls, cv2.COLOR_GRAY2RGB)
            cv2.imshow("img_cls_" + str(int(cth)) + "_" + str(mth) , cv2.addWeighted( img_cls_col, 0.5, img_seg, 0.5, 0 ))

        for cont in contours:
            area_cnt = float( cv2.contourArea(cont) )
            aratio = float( ArcRatio(cont))
            if area_cnt > 1 and aratio < 16 and cv2.pointPolygonTest(cont,(ptc_x,ptc_y),False) > 0 :
                ratio = ( max(area_init, area_cnt) / min(area_init, area_cnt) ) * aratio
                #print(match_val)
                if ratio < ratio_min:
                    #print( "cth, mth, ratio : " + str(cth) + ", " + str(mth) + ", " + str(ratio) )
                    cont_ret = cont
                    ratio_min = ratio
        
        if ratio_min <= 2 :
            break

    return ratio_min, cont_ret


def FindContFromSeed(img_seg, cnt_src) :

    if len(cnt_src) <= 2 : 
        return None

    cont_list = list()
    for xy in cnt_src :
        cont_list.append( [int(xy["x"]), int(xy["y"])] )
    pts_init = np.array(cont_list, np.int32)

    # 処理領域
    rect_init = cv2.boundingRect(pts_init)
    rect_proc = [0,0,img_w,img_h]
    rect_proc[0] = max( rect_init[0] - rect_init[2], 0 )
    rect_proc[1] = max( rect_init[1] - rect_init[3], 0 )
    rect_proc[2] = min( rect_init[2] * 3, img_w - rect_proc[0] )
    rect_proc[3] = min( rect_init[3] * 3, img_h - rect_proc[1] )
    #print(rect_proc)

    for xy in pts_init :
        xy[0] -= rect_proc[0]
        xy[1] -= rect_proc[1]


    # 初期輪郭を整形する
    cont_init = pts_init

    # 画像の切り出し
    img_trm = img_seg[rect_proc[1]:rect_proc[1]+rect_proc[3],rect_proc[0]:rect_proc[0]+rect_proc[2]]

    # if debug_out_lv >= 2 :
    #     cv2.imshow("img_trm", img_trm)

    # 輪郭検出
    ratio_min = 9999.0
    cont_ret = cont_init
    th = 128
    while ratio_min >= 2 and th >= 16:
        ratio, cont_fnd = FindContRet(img_trm, cont_init, ratio_min, th )
        if ratio < ratio_min:
            ratio_min = ratio
            cont_ret = cont_fnd
        th /= 1.4

    if debug_out_lv >= 2 :
        img_trm_copy = img_trm.copy()
        cv2.drawContours( img_trm_copy, [cont_fnd], 0, (255, 255, 255 ), -1 )
        cv2.imshyow("img_trm", img_trm_copy)

    for i in range( len(cont_ret) ):
        cont_ret[i][0][0] += rect_proc[0]
        cont_ret[i][0][1] += rect_proc[1]

    # if debug_out_lv >= 2 :
    #     img_seg_copy = img_seg.copy()
    #     cv2.polylines( img_seg_copy, cont_ret, True, 255, 2 )
    #     cv2.imshow("img_seg", img_seg_copy)

    return cont_ret


############################################################################
## MainFunction
############################################################################

# print(sys.version_info)
start = time.time()

# jsonを読み込み
py_path = os.path.dirname(os.path.abspath(__file__))
json_path = py_path + "\..\sample\_tmp.json"
if len(sys.argv) >= 2:
    json_path = sys.argv[1]
    #print( json_path )
if len(sys.argv) >= 3 :
    debug_out_lv = int(sys.argv[2])
    #print( debug_out_lv )
file_json = open(json_path, 'r') 
json_dict = json.load(file_json) 
file_json.close()

# 画像を読む
file_path = json_dict["imagePath"]
img_org = cv2.imread(file_path)
if img_org is None:
    img_org = cv2.imread(os.path.dirname(json_path) + file_path )
img_h = img_org.shape[0]
img_w = img_org.shape[1]
size_img = dict()
size_img["h"] = img_h
size_img["w"] = img_w

# 先に全体をセグメンテーション
img_seg = cv2.pyrMeanShiftFiltering(img_org, 4, 16, 0 )
img_seg = cv2.medianBlur(img_seg, 3)

# Fixed輪郭の取り出し
cont_array_valid = list()
if "fixedContours" in json_dict :
    for cnt_src in json_dict["fixedContours"] :
        cont_list = list()
        for xy in cnt_src :
            cont_list.append( [int(xy["x"]), int(xy["y"])] )
        cont_array_valid.append( np.array(cont_list, np.int32) )

# 追加する輪郭データ初期値の取り出しと整形
if "addContourSeeds" in json_dict :
    for cnt_src in json_dict["addContourSeeds"] :
        cont_array_valid.append( FindContFromSeed(img_seg, cnt_src) )

cont_array_invalid = list()
if "reductContourSeeds" in json_dict :
    for cnt_src in json_dict["reductContourSeeds"] :
        cont_array_invalid.append( FindContFromSeed(img_seg, cnt_src) )

# 輪郭の整理(必要に応じて結合)
cont_list_Array = ReFineCont(cont_array_valid, cont_array_invalid, img_seg, 4)


# json出力
pts_ary_ret = []
for cont in cont_list_Array:
    pts_ret = []
    for i in range( len(cont) ):
        pt_dic = {}
        pt_dic["x"] = int(cont[i][0][0])
        pt_dic["y"] = int(cont[i][0][1])
        pts_ret.append( pt_dic )
    pts_ary_ret.append(pts_ret)

dict_ret = {}
dict_ret["contours"] = pts_ary_ret

#print(json.dumps(dict_ret, indent=4))
root, ext = os.path.splitext(json_path)
output_path = root + "_Mason" + ext
f = open(output_path, "w")
json.dump(dict_ret,f,indent=4)
f.close()
print_string = json.dumps(dict_ret,indent=4)
print (print_string)

elapsed_time = time.time() - start
#print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")


# 画像のと表示
img_mask = np.zeros((img_h, img_w, 3), np.uint8)
img_mask = cv2.drawContours(img_mask, cont_list_Array, 0, (255,255,255), -1)
img_mask = cv2.bitwise_and( img_seg.copy(), img_mask )

alpha = 0.75
img_ret = cv2.addWeighted(img_mask, alpha, img_seg, 1 - alpha, 0) 
img_ret = cv2.drawContours(img_ret, cont_list_Array, 0, (255,255,255), 1)

cv2.imwrite(root + "_Mason.jpg", img_ret)
if debug_out_lv >= 1:
    cv2.imshow("img_ret", img_ret )
    cv2.waitKey(0)
    cv2.destroyAllWindows()
