from PySide2.QtCore import QObject
import maya.cmds as mc
import os

from PySide2.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QPushButton

#Is this the best way to do this? no. But if set up correctly it should work without a problem.
#if you run into any issues, make sure the folder for this is in the 
#C:\Users\{userName}\Documents\scripts, not in a specific maya version scripts folder
def GetHalfRigAsset() -> str:
    ws = mc.workspace(q=True, rd=True)
    assetPath = os.path.abspath(os.path.join(ws, '../..', 'scripts/MayaAutoRigTechDirect/assets/HalfRig.mb'))

    return assetPath

class Skeleton():
    def __init__(self):
        self.hip = "joint_hip"

        #these 2 are stored so we know what we need to mirror, this is why you shouldn't change the name of the joints
        self.leftShoulder = "joint_l_clavical"
        self.leftThigh = "joint_l_thigh"
        self.SkinCluster = mc.getAttr(mc.listRelatives(self.hip, p = True)[0] + ".Skin")
        print(self.SkinCluster)
        
    def SetUpInitialSkeleton(self):
        print(GetHalfRigAsset())
        mc.file(GetHalfRigAsset(), i = True)
    
    def FinishSkeleton(self, obj: str):
        AllJoints = mc.listRelatives(self.hip, ad =True)

        for joints in AllJoints:
            mc.makeIdentity(joints, a = True, t = True, r = True, s = True, jo = True)
            mc.delete(joints, constructionHistory = True )

        #mirrors the joints
        mc.mirrorJoint(self.leftShoulder, myz = True)

        lShoulderList = mc.listRelatives("joint_l_clavical1", ad = True)
        lShoulderList.append("joint_l_clavical1")
        
        mc.mirrorJoint(self.leftThigh, myz = True)

        lThighList = mc.listRelatives("joint_l_thigh1", ad = True)
        lThighList.append("joint_l_thigh1")

        allItems = lShoulderList + lThighList

        #renames all of the joints to match naming scheme of left side
        for item in allItems:
            newName = item.replace("l","r", 1)

            if "pinkyFinger" in newName or "ringFinger" in newName or "middreFinger" in newName or "pointerpinterFinger" in newName or "thumb" in newName:
                newNum = int(newName[-1]) - 4
                newName = newName.replace(str(newName[-1]), str(newNum))
            else:
                newName = newName.replace("1", "")
            
            mc.rename(item, newName)

            #Freeze transformations and delete the history
            mc.makeIdentity(newName, a = True, t = True, r = True, s = True, jo = True)
            mc.delete(newName, constructionHistory = True )
            
        self.SkinCluster = mc.skinCluster(self.hip, obj)[0]
        print("hip: "+self.hip)
        print("object: "+ obj)
        mc.setAttr(mc.listRelatives(self.hip, p = True)[0] + ".Skin", self.SkinCluster, type = "string")
        print(self.SkinCluster)

    def ResetSkeleton(self):
        rClavical = self.leftShoulder.replace("l", "r", 1)
        rThigh = self.leftThigh.replace("l","r", 1)

        rClavicalList = mc.listRelatives(rClavical, ad = True)
        rClavicalList.append(rClavical)
        rThighList = mc.listRelatives(rThigh, ad = True)
        rThighList.append(rThigh)
        allItems = rClavicalList + rThighList

        for item in allItems:
            mc.removeJoint(item)
        
        mc.delete(self.SkinCluster)



class SkeletonGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.skeleton = Skeleton()
        
        self.masterLayerout = QVBoxLayout()
        self.setLayout(self.masterLayerout)

        self.initSkeletonButton = QPushButton("Create Skeleton")
        self.initSkeletonButton.clicked.connect(self.SetUpSkeleton)
        self.masterLayerout.addWidget(self.initSkeletonButton)

        self.finishSkeleton = QPushButton("Finish Skeleton")
        self.finishSkeleton.clicked.connect(self.FinishSkeleton)
        self.masterLayerout.addWidget(self.finishSkeleton)

        self.resetSkeleton = QPushButton("Reset Skeleton")
        self.resetSkeleton.clicked.connect(self.ResetSkin)
        self.masterLayerout.addWidget(self.resetSkeleton)

    
    def SetUpSkeleton(self):
        print("button works")
        self.skeleton.SetUpInitialSkeleton()
    
    def FinishSkeleton(self):
        selectedItem = mc.ls(sl = True)
        if len(selectedItem) > 1:
            QMessageBox.warning(self, "Warning", "More then 1 object was selected. Please Only select one mesh.")
        elif len(selectedItem) < 1:
            QMessageBox.warning(self, "Warning", "No object was selected. Please Select an object.")
        else: 
            self.skeleton.FinishSkeleton(selectedItem[0])
    
    def ResetSkin(self):
        print("Resetting")
        self.skeleton.ResetSkeleton()


skeleton = SkeletonGUI()
skeleton.show()