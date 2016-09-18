# TODO make this happen
#==============================================================================
#SUB Intro
#==============================================================================
# TODO make this its own gamestate
def Intro:
    lScale = 375
    lz = -60
    lx = 320
    ly = 175
    
    #Get the points that are in the logo
    RESTORE LogoData
    READ NumPts
    FOR n = 1 TO NumPts
        READ InPts(n).x, InPts(n).y, InPts(n).z
    NEXT n
    
    #Get the line data that will make the logo
    RESTORE LineData
    READ NumLines
    FOR n = 1 TO NumLines
        READ Lines(n).StartPt, Lines(n).EndPt
    NEXT n
    
    SCREEN Mode, 0, 1, 0
    if Mode <> 9 :
        WINDOW SCREEN (0, 0)-(639, 349)
    END IF
    
    tx = 0: ty = 0: tz = 0
    
    DO
        tx = tx + 6
        ty = ty - 12
        tz = tz + 3
        
        CALL Rotate(tx, ty, tz)
        RenderLogo
        message 23, "A Y2K Compliant Game...", 1
        PCOPY 1, 0: CLS
        
    LOOP WHILE INKEY$ = ""
    
    XPDx = 320: XPDy = 125: XPDScale = 10
    
    RESTORE XPDData
    READ NumPt
    FOR n = 1 TO NumPt
        READ XPD(n).x, XPD(n).y
     
        XPD(n).x = (XPDScale * XPD(n).x) + XPDx
        XPD(n).y = (XPDScale * (4 - XPD(n).y)) + XPDy
    NEXT n
    
    RESTORE XPDLineData
    READ NumLn
    FOR n = 1 TO NumLn
        READ XPDLine(n).StartPt, XPDLine(n).EndPt
    NEXT n
    
    FOR n = 1 TO NumLn
        PtAx = XPD(XPDLine(n).StartPt).x
        PtAy = XPD(XPDLine(n).StartPt).y
        PtBx = XPD(XPDLine(n).EndPt).x
        PtBy = XPD(XPDLine(n).EndPt).y
     
        LINE (PtAx, PtAy)-(PtBx, PtBy), 15
    NEXT n
    
    #FOR n = 1 TO NumPts
    #    CIRCLE (XPD(n).x, XPD(n).y), 1, 1
    #NEXT n
    
    LINE (0, 115)-(639, 125), 15, B
    LINE (0, 205)-(639, 215), 15, B
    
    PAINT (105, 165), 15, 15            #Paint around the X
    PAINT (220, 145), 15, 15
    PAINT (220, 185), 15, 15
    PAINT (245, 165), 15, 15
    
    PAINT (300, 150), 15, 15            #Paint around the P
    PAINT (300, 190), 15, 15
    PAINT (365, 128), 15, 15
    
    PAINT (400, 165), 15, 15            #Paint around the D
    PAINT (500, 165), 15, 15
    
    PAINT (0, 0), 2, 15
    PAINT (0, 349), 2, 15
    
    x = 320: y = 30: z = -60: Scale = 165
    
    Style = 8
    RESTORE BikeColorData
    FOR n = 1 TO Style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    InitBike
    RotateBike 10, 300, 30
    RotateBar 10, 340, 30
    bike.draw()
    
    x = 520: y = 64: z = -60: Scale = 165
    
    Style = 3
    RESTORE BikeColorData
    FOR n = 1 TO Style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    InitBike
    RotateBike 0, 180, -25
    RotateBar 0, 180, -25
    bike.draw()
    
    x = 120: y = 30: z = -60: Scale = 140
    
    Style = 5
    RESTORE BikeColorData
    FOR n = 1 TO Style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    InitBike
    RotateBike 70, 180, -15
    RotateBar 70, 180, -15
    bike.draw()
    
    message 23, "XPDient Software Solutions", 1
    
    PCOPY 1, 0: CLS
    WHILE INKEY$ = "": WEND
    
END SUB


#==============================================================================
#SUB RenderLogo
#==============================================================================
def RenderLogo:
    #FOR n = 1 TO NumPts
    #    CIRCLE (Pts2D(n).x, Pts2D(n).y), 1, 14
    #NEXT n
    
    FOR n = 1 TO NumLines
        PointA = Lines(n).StartPt
        PointB = Lines(n).EndPt
    
    SELECT CASE n
        CASE 1 TO 36
            col = 4
        CASE 37 TO 84
            col = 15
        CASE 85 TO 129
            col = 1
    END SELECT
    LINE (Pts2D(PointA).x, Pts2D(PointA).y)-(Pts2D(PointB).x, Pts2D(PointB).y), col
    NEXT n
END SUB


LogoData:
DATA 86
DATA -16,14,2       : #Front side of Y
DATA -13,14,2
DATA -13,2,2
DATA -10,2,2
DATA -10,14,2
DATA -7,14,2
DATA -7,0,2
DATA -10,-3,2
DATA -10,-14,2
DATA -13,-14,2
DATA -13,-3,2
DATA -16,0,2

DATA -16,14,-2       : #Back side of Y
DATA -13,14,-2
DATA -13,2,-2
DATA -10,2,-2
DATA -10,14,-2
DATA -7,14,-2
DATA -7,0,-2
DATA -10,-3,-2
DATA -10,-14,-2
DATA -13,-14,-2
DATA -13,-3,-2
DATA -16,0,-2

DATA -4,7,2         : #Front side of 2
DATA -4,10,2
DATA -1,14,2
DATA 1,14,2
DATA 4,10,2
DATA 4,2,2
DATA -1,-5,2
DATA -1,-8,2
DATA 4,-8,2
DATA 4,-14,2
DATA -4,-14,2
DATA -4,-5,2
DATA 1,2,2
DATA 1,10,2
DATA -1,10,2
DATA -1,7,2

DATA -4,7,-2         : #Back side of 2
DATA -4,10,-2
DATA -1,14,-2
DATA 1,14,-2
DATA 4,10,-2
DATA 4,2,-2
DATA -1,-5,-2
DATA -1,-8,-2
DATA 4,-8,-2
DATA 4,-14,-2
DATA -4,-14,-2
DATA -4,-5,-2
DATA 1,2,-2
DATA 1,10,-2
DATA -1,10,-2
DATA -1,7,-2

DATA 8,14,2       : #Front side of K"
DATA 11,14,2
DATA 11,2,2
DATA 13,6,2
DATA 13,14,2
DATA 16,14,2
DATA 16,6,2
DATA 13,0,2
DATA 16,-6,2
DATA 16,-14,2
DATA 13,-14,2
DATA 13,-6,2
DATA 11,-2,2
DATA 11,-14,2
DATA 8,-14,2

DATA 8,14,-2       : #Back side of K"
DATA 11,14,-2
DATA 11,2,-2
DATA 13,6,-2
DATA 13,14,-2
DATA 16,14,-2
DATA 16,6,-2
DATA 13,0,-2
DATA 16,-6,-2
DATA 16,-14,-2
DATA 13,-14,-2
DATA 13,-6,-2
DATA 11,-2,-2
DATA 11,-14,-2
DATA 8,-14,-2


LineData:
DATA 129

DATA 1,2      : #Front Side of Y
DATA 2,3
DATA 3,4
DATA 4,5
DATA 5,6
DATA 6,7
DATA 7,8
DATA 8,9
DATA 9,10
DATA 10,11
DATA 11,12
DATA 12,1
DATA 13,14      : #Back side of Y
DATA 14,15
DATA 15,16
DATA 16,17
DATA 17,18
DATA 18,19
DATA 19,20
DATA 20,21
DATA 21,22
DATA 22,23
DATA 23,24
DATA 24,13

DATA 1,13       : #Connect the front of Y to back of Y
DATA 2,14
DATA 3,15
DATA 4,16
DATA 5,17
DATA 6,18
DATA 7,19
DATA 8,20
DATA 9,21
DATA 10,22
DATA 11,23
DATA 12,24

DATA 25,26          : #Front side of 2
DATA 26,27
DATA 27,28
DATA 28,29
DATA 29,30
DATA 30,31
DATA 31,32
DATA 32,33
DATA 33,34
DATA 34,35
DATA 35,36
DATA 36,37
DATA 37,38
DATA 38,39
DATA 39,40
DATA 40,25

DATA 41,42          : #Back side of 2
DATA 42,43
DATA 43,44
DATA 44,45
DATA 45,46
DATA 46,47
DATA 47,48
DATA 48,49
DATA 49,50
DATA 50,51
DATA 51,52
DATA 52,53
DATA 53,54
DATA 54,55
DATA 55,56
DATA 56,41

DATA 25,41          : #Connect front of 2 to back of 2
DATA 26,42
DATA 27,43
DATA 28,44
DATA 29,45
DATA 30,46
DATA 31,47
DATA 32,48
DATA 33,49
DATA 34,50
DATA 35,51
DATA 36,52
DATA 37,53
DATA 38,54
DATA 39,55
DATA 40,56

DATA 57,58          : #Front side of K
DATA 58,59
DATA 59,60
DATA 60,61
DATA 61,62
DATA 62,63
DATA 63,64
DATA 64,65
DATA 65,66
DATA 66,67
DATA 67,68
DATA 68,69
DATA 69,70
DATA 70,71
DATA 71,57

DATA 72,73          : #Back side of K
DATA 73,74
DATA 74,75
DATA 75,76
DATA 76,77
DATA 77,78
DATA 78,79
DATA 79,80
DATA 80,81
DATA 81,82
DATA 82,83
DATA 83,84
DATA 84,85
DATA 85,86
DATA 86,72

DATA 57,72          : #Connect front of K to back of K
DATA 58,73
DATA 59,74
DATA 60,75
DATA 61,76
DATA 62,77
DATA 63,78
DATA 64,79
DATA 65,80
DATA 66,81
DATA 67,82
DATA 68,83
DATA 69,84
DATA 70,85
DATA 71,86




XPDData:
DATA 32
DATA -15,4
DATA -13,4
DATA -10,1
DATA -7,4
DATA -5,4
DATA -9,0
DATA -5, -4
DATA -7,-4
DATA -10,-1
DATA -13,-4
DATA -15,-4
DATA -11,0
DATA 3,4
DATA 5,2
DATA 5,0
DATA 3,-2
DATA -3,-2
DATA -3,-4
DATA -3,2
DATA 3,2
DATA 3,0
DATA -3,0
DATA 5,4
DATA 13,4
DATA 15,2
DATA 15,-2
DATA 13,-4
DATA 5,-4
DATA 7,1
DATA 13,1
DATA 13,-1
DATA 7,-1

XPDLineData:
DATA 34
DATA 1,2
DATA 2,3
DATA 3,4
DATA 4,5
DATA 5,6
DATA 6,7
DATA 7,8
DATA 8,9
DATA 9,10
DATA 10,11
DATA 11,12
DATA 12,1
DATA 5,13
DATA 13,14
DATA 14,15
DATA 15,16
DATA 16,17
DATA 17,18
DATA 18,7
DATA 7,5
DATA 19,20
DATA 20,21
DATA 21,22
DATA 22,19
DATA 23,24
DATA 24,25
DATA 25,26
DATA 26,27
DATA 27,28
DATA 28,23
DATA 29,30
DATA 30,31
DATA 31,32
DATA 32,29




