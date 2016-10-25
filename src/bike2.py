#!/usr/bin/env python2

import pygame
import random
import os
import sys
import logging

# pymkfgame imports
import math
from pymkfgame.core.game_application import GameApplication
from pymkfgame.gameobj.gameobj import GameObj
from pymkfgame.mkfmath import matrix
from pymkfgame.mkfmath import vector

#import game_state_main_menu
import game_state_playing

###==============================================================================
###FUNCTION coss (x)
###Returns the cosine of x, where x is an angle in degrees
###==============================================================================
### TODO maybe add this to pymkfgame.math?
##def coss(x):
##    val = math.cos(toRad(x))
##    if abs(val) < 0.00001:
##        val = 0.0
##    return val
##
### TODO possibly add to pymkfgame.math
###==============================================================================
###FUNCTION sinn (x)
###==============================================================================
##def sinn(x):
##    sinn = SIN(toRad(x))
##END FUNCTION
##
### TODO possibly add to pymkfgame.math
###==============================================================================
###FUNCTION toRad (x)
###==============================================================================
##def toRad(x):
##    toRad = (x MOD 360) * (3.14159 / 180)
##END FUNCTION
##
##
##
#===========================================================================================================
# TODO get rid of all this hardcoded crap. At the time you made this game, you didn't know how to do file IO
# All of these data points belong in a file

def main():
    # NOTE: Couldn't decide whether to put pygame.init() at this level or in the GameApplication class. It probably belongs in GameApplication (in an Init()) function of sorts..)
    pygame.init()

    game = GameApplication()
    # TODO for release, switch back to changeState(Intro) (we want to start with Intro state; then, from intro, switch into Main Menu))
    #game.changeState(game_state_intro.GameStateImpl.Instance())
    #game.changeState(game_state_main_menu.GameStateImpl.Instance())
    game.changeState(game_state_playing.GameStateImpl.Instance())

    # NOTE timer should be part of application class, too, but this is hack'n'slash.. No time to fix it!!
    prev_time = pygame.time.get_ticks()
    accumulator = 0.0
    dt_s_fixed = 0.015

    while game.isRunning:
        curr_time = pygame.time.get_ticks()
        dt_s = (curr_time - prev_time) / 1000.0
        #print "Curr {}, prev {}, dt {}".format(curr_time, prev_time, dt_s)
        prev_time = curr_time
        accumulator += dt_s

        # ----- Process events
        game.processEvents()

        # ----- Process commands
        game.processCommands()

        # ----- Update stuff
        while accumulator >= dt_s_fixed:
            game.update(dt_s_fixed)
            accumulator -= dt_s_fixed

        # ----- pre-render 
        game.preRenderScene()

        # ----- Draw stuff
        game.renderScene()

        # ----- post-render (e.g. score/overlays)
        game.postRenderScene()

    # Do any engine cleanup here

    # TODO Treat game states here the same way you did in Falldown x64 - they can be "functions" in this file, but each game_state should have its own event handler, input processor, etc
    #MainMenu()



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main()
