# coding:utf-8
import numpy as np
import cv2


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

def ContsAry2Dic( contsAry ) :
    contsDic = []
    for contA in contsAry:
        consD = []
        for i in range( len(contA) ):
            ptD = {}
            ptD["x"] = int(contA[i][0][0])
            ptD["y"] = int(contA[i][0][1])
            consD.append( ptD )
        contsDic.append(consD)

    return contsDic

def ContsDic2Ary( contDic ) :
    contsAry = []
    for contD in contDic :
        contL = []
        for ptD in contD:
            if "x" in ptD and "y" in ptD  :
                ptL = []
                ptL.append( int(ptD["x"]) )
                ptL.append( int(ptD["y"]) )
                contL.append([ptL])
        contsAry.append(np.array(contL))

    return contsAry