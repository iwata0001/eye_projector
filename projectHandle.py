#アンカーポイント生成モデル
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact
from ipywidgets import FloatSlider
import copy
import math
import pywt
import os
import json

from utlLib import isExeption
from mesh2Lib import mesh2
import preDataHandle

featVecsNormalized = preDataHandle.featVecsNormalized
avgHndl = preDataHandle.avgHndl
avgImageVec = preDataHandle.avgImageVec
avgHandleVec_4 = preDataHandle.avgHandleVec_4
stdHandle_EM = preDataHandle.stdHandle_EM
stdImage = preDataHandle.stdImage
avgHandleVec = preDataHandle.avgHandleVec

eigVal_EM = np.load('saves/eigVal_autoHandleGen_EMPCA.npy')
eigVec_EM = np.load('saves/eigVec_autoHandleGen_EMPCA.npy')
indices_EM = np.argsort(eigVal_EM)[::-1]
eigValSum_EM = np.sum(eigVal_EM)

#累積寄与率がcontRateになるまで固有ベクトルを並べる
"""
contRate = 0.7
A = []
temp = 0
for n in range(len(eigVal)):
    temp += eigVal[indices[n]]
    if temp / eigValSum > contRate:
        D = n
        break

#print("D: ", D)

for n in range(D):
    A.append(eigVec[indices[n]])
"""

A_EM = []
temp_EM = 0
contRate = 0.8
for n in range(len(eigVal_EM)):
    temp_EM += eigVal_EM[indices_EM[n]]
    if temp_EM / eigValSum_EM > contRate:
        D_EM = n
        break

for n in range(D_EM):
    A_EM.append(eigVec_EM[indices_EM[n]])

# 並べた固有ベクトルで張られる空間に点を正射影する行列Pを求める
"""
A = np.array(A)
A = A.T
P = np.linalg.inv(A.T @ A) @ A.T
"""

A_EM = np.array(A_EM)
A_EM = A_EM.T
P_EM = np.linalg.inv(A_EM.T @ A_EM) @ A_EM.T

featA = featVecsNormalized.T
featP = np.linalg.inv(featA.T @ featA) @ featA.T

def findEdge(img):
    shape = img.shape
    black = np.zeros_like(img)
    edgeR = [0,0]
    edgeNumR = 0
    edgeL = [0,0]
    edgeNumL = 0
    edgeD = [0,0]
    edgeNumD = 0
    for j in range(shape[1]):
        for i in range(shape[0]):
            if img[i][j] != 255 and edgeNumL == 0:
                edgeNumL +=1
                edgeL[0] +=i
                edgeL[1] +=j
            if img[i][shape[1]-1-j] != 255 and edgeNumR == 0:
                black[i][shape[1]-1-j] = 255
                edgeNumR +=1
                edgeR[0] +=i
                edgeR[1] += (shape[1]-1-j)
        if (edgeNumR > 0) and (edgeNumL > 0):
            break

        for i in range(shape[0]):
            for j in range(shape[1]):
                if img[shape[0]-1-i][j] != 255:
                    edgeNumD +=1
                    edgeD[0] += (shape[0]-1-i)
                    edgeD[1] +=j
            if edgeNumD > 0:
                break

    return {"R":np.array([edgeR[1]/edgeNumR, edgeR[0]/edgeNumR]), 
            "L":np.array([edgeL[1]/edgeNumL, edgeL[0]/edgeNumL]),
            "D":np.array([edgeD[1]/edgeNumD, edgeD[0]/edgeNumD])}

#def project_autoHandleGen(sketch,handle=avgHndl): #skechはcv2.imreadで読み込んだもの
    mesh = mesh2(64,48,sketch)
    mesh.setHandlesOrg(handle, avgHndl)
    mesh.setHandlesDfm(avgHndl)
    mesh.applyHandles()
    img = mesh.deform()
    imgVec = img.reshape(48*64)
    imgVecNormalized = imgVec - avgImageVec

    handleVec = handle.reshape(4*1*2)
    handleVecNormalized = handleVec - avgHandleVec_4

    featureVec = np.append(imgVecNormalized/stdImage, handleVecNormalized/stdHandle)
    avgFeatureVec = np.append(avgImageVec/stdImage, avgHandleVec_4/stdHandle)

    if D != 0:
        x = P @ featureVec
        p = A @ x

        newFeatVec = avgFeatureVec + p
    else:
        newFeatVec = avgFeatureVec

    newImgVec,nokori = np.split(newFeatVec,[48*64])
    feat_x = featP @ p
    newHandleVec = (handleVecsNormalized.T) @ feat_x + avgHandleVec
    #newHandleVec.reshape(preData.H,1,2)

    return(newImgVec*stdImage, newHandleVec)

def project_autoHandleGen_EM(sketch,handle=avgHndl): #skechはcv2.imreadで読み込んだもの
    mesh = mesh2(64,48,sketch)
    mesh.setHandlesOrg(handle, avgHndl)
    mesh.setHandlesDfm(avgHndl)
    mesh.applyHandles()
    img = mesh.deform()
    cv2.imwrite('temp_img/normalizedSketch_gray.png', img)
    imgVec = img.reshape(48*64)
    imgVecNormalized = imgVec - avgImageVec

    handleVec = handle.reshape(4*1*2)
    handleVecNormalized = handleVec - avgHandleVec_4
    initInputHandle = handleVecNormalized/stdHandle_EM

    initInputImg = imgVecNormalized/stdImage
    avgFeatureVec = np.append(avgImageVec/stdImage, avgHandleVec/stdHandle_EM)

    estimated = np.zeros(13*1*2)

    for i in range(100):
        estimated[[2,3,4,5,6,7,24,25]] = initInputHandle
        tempFeatureVec = np.append(initInputImg, estimated) # EMPCAのために最初は平均（０）で残りの次元を埋める　あとは推定値で埋める

        # 途中経過の描画部分　消してもよい
        #############################################################
        '''
        v = avgFeatureVec + tempFeatureVec
        iv, hv = np.split(v,[48*64])
        iv = iv*stdImage
        hv = hv*stdHandle_EM
        img = iv.reshape((48,64))
        img = img.astype(np.uint8)
        img.clip(0,255)
        h = hv.reshape((13,1,2))
        imgc = cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB)
        for pos in h:
            p = (int(pos[0][0]),int(pos[0][1]))
            cv2.circle(imgc, p, 1, (0,0,255), thickness=-1)
        cv2.imwrite('temp_img/empca/empcaIn'+str(i)+'.png', imgc)
        '''
        #############################################################

        if D_EM != 0:
            x = P_EM @ tempFeatureVec
            p = A_EM @ x

            newFeatVec = avgFeatureVec + p
        else:
            newFeatVec = avgFeatureVec

        rtn = tempFeatureVec + avgFeatureVec
        nokori, estimated = np.split(p,[48*64])

        # 途中経過の描画部分　消してもよい
        #############################################################
        '''
        tex = newImgVec*stdImage
        tex = tex.clip(0,255)
        tex = tex.reshape((48,64))
        mesh = mesh2(64,48,tex)
        mesh.setHandlesOrg(avgHandle)
        h = newHandleVec*stdHandle_EM
        h = h.reshape((13,1,2))
        mesh.setHandlesDfm(h)
        mesh.applyHandles()
        img = mesh.deform()
        imgc = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        for pos in h:
            p = (int(pos[0][0]),int(pos[0][1]))
            cv2.circle(imgc, p, 1, (0,0,255), thickness=-1)
        cv2.imwrite('temp_img/empca/empcaOut'+str(i)+'.png', imgc)
        '''
        #############################################################

        

    #newImgVec, newHandleVec = np.split(rtn,[48*64])
    newImgVec, newHandleVec = np.split(newFeatVec,[48*64])

    return(newImgVec*stdImage, newHandleVec*stdHandle_EM)

#newImg = newImgVec.reshape(48,64)
#newImg = np.clip(newImg, 0, 255)
#newImg = newImg.astype(np.uint8)
#cv2.imshow("image", sketch)
#cv2.waitKey()

