#==============================================================================
#SUB OptionsMenu
#==============================================================================
# TODO make this its own game state
def OptionsMenu():
    CLS
    one = 20: two = 50
    max = 7
    flag = 1
    
    DO
        message 1, STRING$(80, "-"), 1
        message 2, "Trick Biker - Options", 1
        message 3, STRING$(80, "-"), 1
        message 23, "<I> and <K> select, <Enter> confirms selection, <Esc> exits", 1
        
        
        LOCATE 5
        if DrawPoints == -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "Draw Debug Points"; TAB(two); Status$
        
        LOCATE 7
        if Track3D == -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "3D Track"; TAB(two); Status$
        
        LOCATE 9
        if DoRunSummary == -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "Do Run Summary"; TAB(two); Status$
        
        LOCATE 11
        if CrowdOn == -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "Draw Crowd (not implemented)"; TAB(two); Status$
        
        # Note: row 13 is removed. It was Vsync, but we're not using that
        LOCATE 15
        if SloMo == -1 : Status$ = "On" else: Status$ = "Off"
        PRINT TAB(one); "Slow-Motion Tricks"; TAB(two); Status$
        
        LOCATE 17
        PRINT TAB(one); "View Intro Again"
        
        flagY = (flag * 2 * 14) + 14 * 2
        LINE (80, flagY)-(560, flagY + 14), 4, B
        
        PCOPY 1, 0: CLS
        
        a$ = INKEY$
        SELECT CASE UCASE$(a$)
            CASE "I"
                flag = flag - 1
                if flag < 1 : flag = max
        
            CASE "K"
                flag = flag + 1
                if flag > max : flag = 1
        
            CASE CHR$(13)
                SELECT CASE flag
                    CASE 1
                        if DrawPoints == 0 :
                            DrawPoints = -1
                        else:
                            DrawPoints = 0
                        END IF
                 
                    CASE 2
                        if Track3D == 0 :
                            Track3D = -1
                        else:
                            Track3D = 0
                        END IF
                 
                    CASE 3
                        if DoRunSummary == 0 :
                            DoRunSummary = -1
                        else:
                            DoRunSummary = 0
                        END IF
                 
                    #Note: case 5 (vsync) was removed
                    CASE 6
                        if SloMo == 0 :
                            SloMo = -1
                        else:
                            SloMo = 0
                        END IF
        
                    CASE 7
                        CALL Intro
                        Scale = 175
                    END SELECT
        
            CASE CHR$(27)
                EXIT SUB
        END SELECT
        
    LOOP
END SUB



