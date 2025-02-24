import numpy as np
import cv2
from scipy import misc
import os 
from data_processing.m_im_util import sdmkdir,to_rgb3b
from sklearn import metrics
#import rasterio
#from rasterio import mask, features, warp

def show_heatmap_on_image(img,mask):
    mask = np.uint8(mask)
    heatmap = cv2.applyColorMap(mask, 3)  #Jet is 2, winter is 3 8 = cool
    heatmap = np.float32(heatmap) / 255
    print(heatmap.shape)
    img = np.float32(img)/255
    cam = heatmap* 0.5+ np.float32(img)
    return np.uint8(cam*255)
def draw(im,ratio): 
    font = cv2.FONT_HERSHEY_SIMPLEX 
    cv2.putText(im,'%.02f'%(ratio),(10,200), font, 3,(255,255,255),4) 
    return im 

def show_plainmask_on_image(oim,mask):
    #mask = np.float32(mask)/255
    mask = np.uint8(mask)
    mask = (mask>=150).astype(np.float)
    #mask[mask>=0.5] =1
    im = oim.astype(np.float)
    if im.ndim ==2:
        im = to_rgb3b(im)
    im = im 
    im[:,:,1] = im[:,:,1] + mask*200
    im[im>255] = 255
    return im.astype(np.uint8)
def visdir(imdir,maskdir,visdir,pimlist=[]):
    
    sdmkdir(visdir)    
    imlist=[]
    imnamelist=[]
    print(imdir)
    for root,_,fnames in sorted(os.walk(maskdir)):
        print(root,fnames)
        for fname in fnames:
            if fname.endswith('.png'):
                if len(pimlist) == 0 or fname[:-4] in pimlist:
                    pathA = os.path.join(imdir,fname)
                    pathB = os.path.join(maskdir,fname)
                    imlist.append((pathA,pathB,fname))
                    imnamelist.append(fname)
    for pathA,pathB,fname in imlist:
        A = misc.imread(pathA)
        B = misc.imread(pathB)
        #vim = show_heatmap_on_image(A,B)
        vim = show_plainmask_on_image(A,B)
        misc.imsave(os.path.join(visdir,fname),np.append(A,vim,axis=1))
def visdir2(imdir,GT,maskdir,visdir,pimlist=[]):
    sdmkdir(visdir)    
    imlist=[]
    imnamelist=[]
    for root,_,fnames in sorted(os.walk(maskdir)):
        for fname in fnames:
            if fname.endswith('.png'):
                if not pimlist or fname[:-4] in pimlist:
                    pathA = os.path.join(imdir,fname)
                    pathGT = os.path.join(GT,fname)
                    pathmask = os.path.join(maskdir,fname)
                    imlist.append((pathA,pathGT,pathmask,fname))
                    imnamelist.append(fname)
    print(imlist)
    sz = 1500 
    count=0
    for pathA,pathB,pathmask,fname in imlist:
        A = misc.imread(pathA).astype(np.uint8)
        GT = misc.imread(pathB)
        mask = misc.imread(pathmask)
        A = misc.imresize(A,(sz,sz))
        GT = misc.imresize(GT,(sz,sz))
        mask = misc.imresize(mask,(sz,sz))
        fpr, tpr, thresholds = metrics.roc_curve(GT.ravel(), mask.ravel(), pos_label=255)
        auc =  metrics.auc(fpr, tpr)
        GTv = show_plainmask_on_image(A,GT)
        #maskv = show_plainmask_on_image(A,mask)
        maskv = show_heatmap_on_image(A,mask)
        maskv = draw(maskv,auc)
        #misc.imsave(os.path.join(visdir,fname),np.hstack((A,maskv,GTv)))#np.append(np.append(A,GTv,axis=1),maskv,axis=1))
        #misc.imsave(os.path.join(visdir,fname),maskv)
        misc.imsave(os.path.join(visdir,str(count)+'.png'),maskv)
        count=count+1
        #misc.imsave(os.path.join(visdir,fname),A)#np.append(np.append(A,GTv,axis=1),maskv,axis=1))
def visAB(root,name,imlist= []):
    
    A = root + '/A/'
    B = root + '/res/' + name +'/'
    vis = root + '/vis/'+name+'/'
    visdir(A,B,vis,imlist)
def visABC(root,name,imlist=[]):
    print('VISABC Visualizing:' + name)
    A = root + '/A/'
    B = root + '/B/'
    res = root + '/res/' + name +'/'
    vis = root + '/vis_all/'+name+'/'
    visdir2(A,B,res,vis,imlist)
def AUC(root,name,pimlist = []):

    A = root + '/A/'
    B = root + '/B/'
    res = root + '/res/' + name +'/'
    imlist=[]
    imnamelist=[]
    for root,_,fnames in sorted(os.walk(res)):
        for fname in fnames:
            if fname.endswith('.png'):
                if not pimlist or fname[:-4] in pimlist:
                    pathA = os.path.join(A,fname)
                    pathGT = os.path.join(B,fname)
                    pathmask = os.path.join(res,fname)
                    imlist.append((pathA,pathGT,pathmask,fname))
                    imnamelist.append(fname)

    AUC =[]    
    for pathA,pathB,pathmask,fname in imlist:
        GT = misc.imread(pathB)
        mask = misc.imread(pathmask)
        fpr, tpr, thresholds = metrics.roc_curve(GT.ravel(), mask.ravel(), pos_label=255)
        auc =  metrics.auc(fpr, tpr)
        #maskv = show_plainmask_on_image(A,mask)
        AUC.append((fname,auc))

    return AUC
'''
def visTIF(root,name):

    print('VISTIF Visualizing:' + name)
    A = root + '/A/'
    B = root + '/B/'
    tif = root + '/tif/'
    res = root + '/res/' + name +'/'
    tifres = root + '/tifres/'+name+'/'
    sdmkdir(tifres)

    imlist=[]
    imnamelist=[]
    for root,_,fnames in sorted(os.walk(res)):
        for fname in fnames:
            if fname.endswith('.png'):
                fname = fname[:-4]
                pathA = os.path.join(tif,fname)
                pathGT = os.path.join(B,fname)
                pathmask = os.path.join(res,fname)
                imlist.append((pathA,pathGT,pathmask,fname[:-4]))
                imnamelist.append(fname)
    print imnamelist
    for pathA,pathB,pathmask,fname in imlist:
        print fname
        GT = misc.imread(pathB+'.png')
        mask = misc.imread(pathmask+'.png')
        tifim = rasterio.open(pathA+'.tif')
        outmeta = tifim.meta.copy()
        outmeta.update({"count":outmeta["count"]+2})
        X = tifim.read()

        mask = np.expand_dims(mask,axis=0)
        GT = np.expand_dims(GT,axis=0)
        X = np.concatenate((X,GT,mask),axis =0)
        with rasterio.open(tifres+fname+'.tif',"w",**outmeta) as dest:
            dest.write(X) 

        print X.shape
'''
