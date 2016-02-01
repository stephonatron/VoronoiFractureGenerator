import maya.cmds as cmds
import random as random
import math as math

window_name = "FractureGenerator"

if cmds.window( window_name, exists = True ):
    cmds.deleteUI( window_name, window = True )
    
window = cmds.window( window_name, title = "Fracture Generator", widthHeight = (300, 600))

tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

child1 = cmds.columnLayout( width = 600 )

cmds.frameLayout( collapsable = True, label = "Basic Voronoi Fracture", width = 600)
cmds.text( label='Please select 1 mesh to fracture.' )
cmds.intSliderGrp('basicDensity',label="Density", field=True, min=2, max=100, value=6)
cmds.button( label = "Basic Fracture", command = ('voroBasic()'))
cmds.setParent( '..')

cmds.frameLayout( collapsable = True, label = "Local Voronoi Fracture", width = 600)
cmds.text( label='Please select 1 vertex as a focal point for your fracture.' )
cmds.intSliderGrp('localDensity',label="Density", field=True, min=2, max=50, value=6)
cmds.button( label = "Local Fracture", command = ('voroLocal()'))
cmds.setParent( '..')

cmds.setParent( '..')

#child2 = cmds.columnLayout( width = 600 )
#cmds.button( label = "Voronoi Fracture", command = ('voroBasic()'))

cmds.tabLayout( tabs, edit=True, tabLabel=((child1, 'Voronoi')) )

cmds.setParent( '..' )

cmds.showWindow( window )

#basic voronio fracture
def voroBasic():
    
    density = cmds.intSliderGrp( 'basicDensity', query = True, value = True)
    selection = cmds.ls( selection = True )
    seeds = []        
     
    if len( selection ) == 1:
        shape = selection[0]
        bbox = cmds.exactWorldBoundingBox( shape )
        
        for i in range(density):
            seed = cmds.spaceLocator( p = ( 0, 0, 0), a = True )[0]
            cmds.move( random.uniform( bbox[0], bbox[3] ), random.uniform( bbox[1], bbox[4] ), random.uniform( bbox[2], bbox[5] ), a = True )
            cmds.scale( 0.1, 0.1, 0.1, a = True, ocp = True )
            seeds.append( seed )
            
        for i in range ( 0, len(seeds)):
            
            shapeCopy = cmds.duplicate( shape ) 
            
            for j in range ( 0, len(seeds)):
                    
                if i != j:
                    
                    voronoiFracture( i, j, seeds, shapeCopy )
                    
        cmds.select( shape )
        cmds.delete()
        
        cmds.select( *seeds )
        cmds.delete()
        
    elif( len( selection ) > 1 ):
        print( 'error: please select only 1 object' )
        
    else:
        print( 'error: please select an object' )
        
#voronoi fracture around a vertex
def voroLocal():
    
    density = cmds.intSliderGrp( 'localDensity', query = True, value = True)
    density = density * 10
    selectedVerts = cmds.ls( sl = True )
    selectedMesh = selectedVerts[0].split('.')
    seeds = []        
     
    if len( selectedVerts ) == 1:
        shape = selectedVerts[0]
        bbox = cmds.exactWorldBoundingBox( selectedMesh[0] )
        
        for i in range( density ):
            vtx = cmds.xform( selectedVerts[0], q = True, ws = True, t = True )
            seed = cmds.spaceLocator( p = ( 0, 0, 0), a = True )[0]
            cmds.move( random.uniform( vtx[0] - 0.1, vtx[0] + 0.1 ), random.uniform( vtx[1] - 0.1, vtx[1] + 0.1 ), random.uniform( vtx[2] - 0.1, vtx[2] + 0.1 ), a = True )
            cmds.scale( 0.1, 0.1, 0.1, a = True, ocp = True )
            
            seedL = cmds.xform( seed, q = True, ws = True, t = True )
            
            if( seedL[0] > bbox[0] and seedL[0] < bbox[3] and seedL[1] > bbox[1] and seedL[1] < bbox[4] and seedL[2] > bbox[2] and seedL[2] < bbox[5] ): 
                seeds.append( seed )
            
            else:
                cmds.select( seed )
                cmds.delete()
        
        
        print(len(seeds))    
        for i in range ( 0, len(seeds)):
            
            meshCopy = cmds.duplicate( selectedMesh[0] ) 
            
            for j in range ( 0, len(seeds)):
                    
                if i != j:
                    
                    voronoiFracture( i, j, seeds, meshCopy )
                    
        cmds.select( selectedMesh[0] )
        cmds.delete()
        
        cmds.select( *seeds )
        cmds.delete()
        
    elif( len( selection ) > 1 ):
        print( 'error: please select only 1 vertex' )
        
    else:
        print( 'error: please select a vertex' )
        

def voronoiFracture( i, j, seeds, shapeCopy ):
    
    p1 = cmds.xform( seeds[j], q = True, ws = True, t = True )
    p2 = cmds.xform( seeds[i], q = True, ws = True, t = True )   
    
    #cutting position
    planePos = getVecPoint( p1, p2, 0.5 )
    
    #calculate unit vector
    vec = getVector( p1, p2 )
    vecMag = magnitude( vec )
    
    vecNorm = [ 0, 0, 0 ]
    vecNorm[0] = vec[0] / vecMag 
    vecNorm[1] = vec[1] / vecMag 
    vecNorm[2] = vec[2] / vecMag 
    
    #calculate cutting angles
    rX = -math.degrees( math.asin( vecNorm[1]))
    rY = math.degrees( math.atan2( vecNorm[0], vecNorm[2] ))
    
    #cut the shape
    cmds.select( shapeCopy )    
    cmds.polyCut( constructionHistory = False, deleteFaces = True, pc = planePos, ro = ( rX, rY, 0 ) )
    cmds.polyCloseBorder( constructionHistory = False )
        
#calculate a vector from two points    
def getVector( pointA, pointB ):
    
    vec = [0, 0, 0]
    
    vec[0] = pointB[0] - pointA[0]
    vec[1] = pointB[1] - pointA[1]
    vec[2] = pointB[2] - pointA[2]
    
    return vec
    
#calculate the magnitude of a vector
def magnitude( vec ):
    
    mag = ( vec[0] ** 2 ) + ( vec[1] ** 2 ) + ( vec[2] ** 2 )
    mag = mag ** 0.5
    
    return mag
    
#calculate a point on a line
def getVecPoint( pointA, pointB, pos ):
    
    point = [ 0, 0, 0 ]
    
    point[0] = pointA[0] + ( pos * ( pointB[0] - pointA[0] ))
    point[1] = pointA[1] + ( pos * ( pointB[1] - pointA[1] ))
    point[2] = pointA[2] + ( pos * ( pointB[2] - pointA[2] ))
    
    return point