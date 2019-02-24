# coding:utf-8
import sys
import os
import time
import json 
import uuid
import copy
import shutil
from collections import namedtuple
import numpy as np
import cv2

import mason_core as wshc
import mason_tools as wsht


# バージョン情報
THIS_VERSION = "0.0.1"

# sessionを保持するDictionary
global sessionDict
sessionDict = {} 

# ワークDirectory
pathWorkDirRoot = os.path.dirname(os.path.abspath(__file__)) + "/work/"

SessionData = namedtuple("SessionData", ("pathSrcImg", "pathWorkDir", "imgSrc", "imgSeg"))

def Init() :
    print(__file__ + " Ver." + THIS_VERSION)    
    print("  " + str(sys.version_info))
    print("  opencv : " + cv2.__version__) 
    if os.path.isdir(pathWorkDirRoot) == False:
        os.makedirs(pathWorkDirRoot)
    return
    
def SocketExecute( reqJson ) :
    if wshc.debug_out_lv >= 1 :
        reqJson_dumps = json.dumps(reqJson, indent=2, separators=(',', ': '))
        print("reqJson : \n" + reqJson_dumps)
        fw = open(pathWorkDirRoot + "req.Json",'w')
        json.dump(reqJson, fw,  indent=2, separators=(',', ': '))

    resJson = {}
    if "reqCode" not in reqJson :
        resJson["resCode"] = -1
    else :
        if reqJson["reqCode"] == 1000 :
            resJson = ReqSetImage( reqJson )
        elif reqJson["reqCode"] == 2000 :
            resJson = ReqProcCore( reqJson )
        elif reqJson["reqCode"] == -1 :
            resJson = ReqClose( reqJson )

            
    if wshc.debug_out_lv >= 1 :
        resJson_dumps = json.dumps(resJson, indent=2, separators=(',', ': '))
        print("resJson : \n" + resJson_dumps)
        fw = open(pathWorkDirRoot + "res.Json",'w')
        json.dump(resJson, fw,  indent=2, separators=(',', ': '))

    return resJson

def FindSessionData( reqJson ):
    sessionID = None
    sd = None
    resJson = {}
    resJson["resCode"] = -1
    if "sessionID" in reqJson and reqJson["sessionID"] in sessionDict:
        sessionID = reqJson["sessionID"]
        resJson["resCode"] = 0
        resJson["sessionID"] = sessionID
        sd = sessionDict[sessionID]
    
    return sessionID, sd, resJson

def ReqSetImage( reqJson ) :

    resJson = {}
    resJson["resCode"] = 0
    if "imagePath" not in reqJson :
        resJson["resCode"] = -1
    else :
        sessionID = str(uuid.uuid4())
        resJson["sessionID"] = sessionID

        sd = copy.deepcopy(SessionData)
        sd.pathSrcImg = reqJson["imagePath"]
        sd.imgSrc = cv2.imread(sd.pathSrcImg)

        if not sd.imgSrc is None:
            
            # 先に全体をセグメンテーション
            sd.imgSeg = wshc.MakeSegImage(sd.imgSrc )
            sd.pathWorkDir = pathWorkDirRoot + sessionID + "/"
            os.makedirs(sd.pathWorkDir)
            cv2.imwrite( sd.pathWorkDir + "seg.jpg", sd.imgSeg)

            sessionDict[sessionID] = sd
            if wshc.debug_out_lv >= 1 :
                print("active session : \n  " + str(sessionDict))
        
        else :
            resJson["resCode"] = -1

    return resJson

def ReqProcCore( reqJson ) :

    _, sd, resJson = FindSessionData( reqJson )
    if sd != None :
        # Fixed輪郭の取り出し
        cont_array_valid = list()
        if "fixedContours" in reqJson :
            for cnt_src in reqJson["fixedContours"] :
                cont_list = list()
                for xy in cnt_src :
                    cont_list.append( [int(xy["x"]), int(xy["y"])] )
                cont_array_valid.append( np.array(cont_list, np.int32) )

        # 処理領域をマスキング
        imgBrack = np.zeros((sd.imgSeg.shape[0], sd.imgSeg.shape[1], 3), np.uint8)
        imgMask = cv2.drawContours(imgBrack.copy(), cont_array_valid, -1, (255,255,255), -1)

        # 追加する輪郭データ初期値の取り出しと整形
        if "addContourSeeds" in reqJson :
            for cnt_src in reqJson["addContourSeeds"] :
                imgSrcBG = cv2.bitwise_and( sd.imgSrc, cv2.bitwise_not( imgMask ) )  
                imgSegBG = cv2.bitwise_and( sd.imgSeg, cv2.bitwise_not( imgMask ) )  
                if wshc.debug_out_lv >= 1 :
                    cv2.imwrite( sd.pathWorkDir + "imgMask.jpg", cv2.bitwise_not( imgMask ))
                    cv2.imwrite( sd.pathWorkDir + "imgSrcBG.jpg", imgSrcBG)
                    cv2.imwrite( sd.pathWorkDir + "imgSegBG.jpg", imgSegBG)

                contRet = wshc.FindContFromSeed(imgSrcBG, cnt_src)

                # contRet = wshc.FindContFromSeed(imgSegBG, cnt_src)
                # if len( contRet ) == 0 :
                #     contRet = wshc.FindContFromSeed(imgSrcBG, cnt_src)
                cont_array_valid.append( contRet )

        cont_array_invalid = list()
        if "reductContourSeeds" in reqJson :
            for cnt_src in reqJson["reductContourSeeds"] :    
                imgSrcFG = cv2.bitwise_and( sd.imgSrc, imgMask )
                imgSegFG = cv2.bitwise_and( sd.imgSeg, imgMask )      
                if wshc.debug_out_lv >= 0 :
                    cv2.imwrite( sd.pathWorkDir + "imgMask.jpg", imgMask)
                    cv2.imwrite( sd.pathWorkDir + "imgSrcFG.jpg", imgSrcFG)
                    cv2.imwrite( sd.pathWorkDir + "imgSegFG.jpg", imgSegFG)

                contRet = wshc.FindContFromSeed(imgSrcFG, cnt_src)

                # contRet = wshc.FindContFromSeed(imgSegFG, cnt_src) 
                # if len( contRet ) == 0 :
                #     contRet = wshc.FindContFromSeed(imgSrcFG, cnt_src) 
                cont_array_invalid.append( contRet )

        # 輪郭の整理(必要に応じて結合)
        cont_list_Array = wshc.ReFineCont(cont_array_valid, cont_array_invalid, sd.imgSeg, 4)

        # json出力
        resJson["contours"] = wsht.ContsAry2Dic(cont_list_Array)

    if wshc.debug_out_lv >= 2 :
        cv2.waitKey(0)

    return resJson

def ReqClose( reqJson ) :

    sessionID, sd, resJson = FindSessionData( reqJson )
    if sd != None :
        shutil.rmtree(sd.pathWorkDir)
        del sessionDict[sessionID]

        if wshc.debug_out_lv >= 1 :
            print("active session : \n  " + str(sessionDict))

    return resJson


def MakeDebugImg( imgSeg, conts ):

    imgMask = np.zeros((imgSeg.shape[0], imgSeg.shape[1], 3), np.uint8)
    imgMask = cv2.drawContours(imgMask, conts, -1, (255,255,255), -1)
    imgMask = cv2.bitwise_and( imgSeg.copy(), imgMask )

    alpha = 0.75
    imgRet = cv2.addWeighted(imgMask, alpha, imgSeg, 1 - alpha, 0) 
    imgRet = cv2.drawContours(imgRet, conts, 0, (255,255,255), 1)

    return imgRet

def SampleExecute( json_path ) :
    start = time.time()


    # jsonを読み込み
    print( "load json : " + json_path )
    file_json = open(json_path, 'r') 
    reqJson = json.load(file_json) 
    file_json.close()

    # 画像を設定
    reqJson["reqCode"] = 1000
    resJson = SocketExecute(reqJson)
    sessionID = resJson["sessionID"]


    # 処理実行    
    reqJson["reqCode"] = 2000
    reqJson["sessionID"] = sessionID
    resJson = SocketExecute(reqJson)

    # 表示用画像の作成
    img_ret = MakeDebugImg( sessionDict[sessionID].imgSeg, wsht.ContsDic2Ary( resJson["contours"] ) )

    # sessionを閉じる
    reqJson["reqCode"] = -1
    resJson = SocketExecute(reqJson)

    # 画像の表示
    if wshc.debug_out_lv >= 1:
        cv2.imshow("img_ret", img_ret )
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return

############################################################################
## MainFunction
############################################################################

if __name__ == "__main__":

    Init()

    wshc.debug_out_lv = 2
    reqJson = pathWorkDirRoot + "sample.Json"

    args = sys.argv

    print( "args : " + str(args) + "\n")
    if len(args) < 2 and os.path.exists(reqJson) == False :
        print("following arguments are required")  
        print("  1st arg : input_json_path.")  
    else :        
        if len(sys.argv) >= 2 :
            reqJson = sys.argv[1]
        if len(sys.argv) >= 3 :
            wshc.debug_out_lv = int(sys.argv[2])

        SampleExecute(reqJson)
