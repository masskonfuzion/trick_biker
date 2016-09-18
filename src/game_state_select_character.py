#==============================================================================
class BikeStyle(object):
    def __init__(self):
        spokeColor = ColorType()        # BikeCol(4)
        tireColor = ColorType()         # BikeCol(2)
        frameColor = ColorType()        # BikeCol(1) ?? TODO: verify frame color
        barColor = ColorType()          # BikeCol(2) ?? TODO: verify handlebar color

#==============================================================================
#SUB SelectBike
#==============================================================================
# TODO make this its own game state (I think). It belongs either at the end of the MainMenu state, or as its own state, or at the beginning of Playing (probably its own state)
def SelectBike:
    CLS
    ang = 0
    Tzf = 0: Tzh = Tzf
    x = 320: y = 130: Scale = 336: Style = 1: Txf = 0: Txh = Txf
    GOSUB Update
    
    DO
    message 1, STRING$(80, "-"), 1
    message 2, "Trick Biker - Select Bike", 1
    message 3, STRING$(80, "-"), 1
    message 23, "<J> and <L> select, <Enter> confirms selection.", 1
    
    a$ = INKEY$
    SELECT CASE UCASE$(a$)
        CASE "J"
            Style = Style - 1
            if Style < 1 : Style = MaxBikes
            GOSUB Update
        CASE "L"
            Style = Style + 1
            if Style > MaxBikes : Style = 1
            GOSUB Update
        CASE CHR$(13)
            BikeStyle = Style
            RiderName$ = msg
            EXIT SUB
        CASE CHR$(27)
            Quit = True
            EXIT SUB
    END SELECT
    
    SELECT CASE Style
        CASE 1
            msg = q + "Gnarly" + q + " Charlie Robinson"
        CASE 2
            msg = "Upton " + q + "Ups" + q + " Malone"
        CASE 3
            msg = "* Justin Grady *"
        CASE 4
            msg = "Abner Brown"
        CASE 5
            msg = "* John Turner *"
        CASE 6
            msg = "Carl Greene"
        CASE 7
            msg = "David Gonzalez"
        CASE 8
            msg = "*** Lou Herard ***"
        CASE 9
            msg = "Willie the Wildcat"
        CASE 10
            msg = "Mike " + q + "Blues" + q + " Klues"
        CASE 11
            msg = "Jamal Jenkins"
        CASE 12
            msg = "Ultimus"
        CASE 13
            msg = "Popeye"
        CASE else:
            msg = ""
    END SELECT
    
    message 5, msg, 1
    
    ang = ang + 6 MOD 360
    #ang = 90
    Tyf = ang: Tyh = Tyf
    
    CALL DrawTrophies(NumTrophies(Style), 500)
    CALL RotateBike(Txf, Tyf + 180, Tzf)
    CALL RotateBar(Txh, Tyh + 180, Tzh)
    bike.draw()
    
    LOCATE 16, 25: PRINT "Speed"
    LOCATE 18, 25: PRINT "Jump"
    bx = 270: w = 7
    maxjmp = 2.8: maxspeed = 22 #these were taken from DATA
    
    by1 = 15 * 14 + 2         #spd
    by2 = 17 * 14 + 2         #jmp
    LINE (bx - 1, by1)-(bx + 101, by1 + w), 14, B
    LINE (bx, by1 + 1)-(bx + 100 * Biker.maxspd / maxspeed, by1 + w - 1), 6, BF
    
    LINE (bx - 1, by2)-(bx + 101, by2 + w), 14, B
    LINE (bx, by2 + 1)-(bx + 100 * Biker.jump / maxjmp, by2 + w - 1), 6, BF
    
    PCOPY 1, 0: CLS
    LOOP
    
    
Update:
    RESTORE BikeColorData
    FOR n = 1 TO Style
        READ BikeCol(1), BikeCol(2), BikeCol(3), BikeCol(4)
    NEXT n
    
    RESTORE BikerData
    FOR n = 1 TO Style
        READ Biker.maxspd, Biker.jump, Biker.pump, Biker.turn
    NEXT n
    
    RETURN
END SUB

BikeColorData: # TODO put these bike colors into the bike class
#Format BodyCol1, BodyCol2, FrontSpokeCol,BackSpokeCol
DATA 15,1,15,15   : #Type 1  - Standard bike
DATA 9,14,6,6     : #Type 2  - Standard bike 2
DATA 7,7,8,8      : #Type 3  - Justin Grady's Chrome Bike
DATA 4,12,1,1     : #Type 4  - Standard bike 3
#DATA 9,13,5,8     : #Type 5  - John Turner's Haro Shredder
DATA 1,1,5,8      : #John Turner's Haro Shredder
DATA 3,11,2,10    : #Type 6  - Standard bike 4
DATA 14,6,15,1    : #Type 7  - Standard bike 5
DATA 8,4,7,7      : #Type 8  - Lou Herard's Schwinn Predator
DATA 15,7,14,1    : #Type 9  - Standard bike 6: Wheeling Special
DATA 1,9,11,11    : #Type 10 - Standard bike 7
DATA 6,5,5,6      : #Type 11 - Standard bike 8

DATA 4,4,4,4      : #Ultimus
DATA 10,15,14,14  : #Popeye

BikerData:
#Format: maxspd, jump, pump, turn
DATA 17,2.2,3,45  : #Gnarly Robinson
DATA 15,2.8,3,45  : #Upton "Ups" Malone
DATA 22,1.7,2,45  : #Justin Grady
DATA 19,1.95,2,45  : #Abner Brown
DATA 18,2.2,3,45  : #John Turner
DATA 21,1.8,3,45  : #Carl Greene
DATA 22,1.7,3,45 : #David Gonzalez
DATA 18,2.1,3,45  : #Lou Herard
DATA 21,1.75,4,45  : #Willie the Wildcat
DATA 16,2.35,2,45 : #Mike "Blues" Klues
DATA 20,1.8,3,45  : #Jamal Jenkins
DATA 18,2.0,2,90  : #Ultimus (secret character)
DATA 18,2.1,3,90  : #Popeye



# TODO Move this to wherever the player select happens (I believe either main menu, or playing state)
#==============================================================================
#SUB DrawTrophies (NumToDraw, StartX)
#==============================================================================
def DrawTrophies(NumToDraw, StartX):
    StartY = 50
    Tscale = 3
    
    RESTORE TrophyData
    READ NumTPts
    
    DIM Trophy(1 TO NumTPts) AS Point2D
    
    FOR n = 1 TO NumTPts
        READ Trophy(n).x, Trophy(n).y
    NEXT n
    
    FOR n = 1 TO NumTPts
        Trophy(n).x = Tscale * Trophy(n).x
        Trophy(n).y = Tscale * (8 - Trophy(n).y)
    NEXT n
    
    RESTORE TrophyLineData
    READ NumTLns
    
    DIM TrophyLines(1 TO NumTLns) AS LineType
    FOR n = 1 TO NumTLns
        READ TrophyLines(n).StartPt, TrophyLines(n).EndPt
    NEXT n
    
    TInCol = 14
    TOutCol = 6
    
    FOR c = 0 TO (NumToDraw - 1)
    FOR n = 1 TO NumTLns
        PtAx = (Trophy(TrophyLines(n).StartPt).x + StartX + (40 * c))
        PtAy = (Trophy(TrophyLines(n).StartPt).y + StartY)
        PtBx = (Trophy(TrophyLines(n).EndPt).x + StartX + (40 * c))
        PtBy = (Trophy(TrophyLines(n).EndPt).y + StartY)
    
        LINE (PtAx, PtAy)-(PtBx, PtBy), TOutCol
    NEXT n
    
    PAINT (PtAx + 3.5, PtAy), TInCol, TOutCol
    NEXT c
END SUB


TrophyData:
DATA 14     : #Number of points
DATA-4,7
DATA 4,7
DATA 3.5,5
DATA 3,4
DATA 2,3
DATA 1,2
DATA 1,1
DATA 3,-0
DATA -3,-0
DATA -1,1
DATA -1,2
DATA -2,3
DATA -3,4
DATA -3.5,5

TrophyLineData:
DATA 14
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
DATA 12,13
DATA 13,14
DATA 14,1
