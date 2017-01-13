# Trick Biker (Prototype)
A remake of a game I made in high school. It's a "3D-in-2D" wireframe, riderless BMX tricking game, developed in Python/Pygamej, with a hand-written engine (including 3D math).

## Technical Notes
This prototype is written in Python 2.  I haven't tested it with Python 3, so I have no idea if it will work (it probably won't.. For sure, any `print` statements will fail, without updating them to work across Python versions).

## About the Project

### Overview
This project is really a prototype of a bigger-badder Trick Biker remake to come in the future.  That bigger-badder remake will feature a rider, and better physics, graphics, scenery, levels, input/controls, etc.  (likely written in Unity).

The original game was written in QBASIC.  The riderless design was inspired by [~~Uniracers on SNES~~](https://en.wikipedia.org/wiki/Uniracers). <- False.  The riderless design was inspired by the fact that I did not know how to animate a rider at the time I made the original game, which was when I was in high school.

Also, in the original game, the bike's wheels did not roll.  Basically, I knew nothing of vector or matrix math, or graphics or physics, at the time I wrote the original game.  Nevertheless, my friends liked the game, and that was enough for me.  (But then, years passed, during which time I strayed away from game development.  Now I am getting back into it, and I decided to reboot the game that got me started with gamedev in the first place.)

This project is very much a work in progress, and is pretty ugly/incomplete at the moment..  No, I'm serious.  **DISCLAIMER**:  The source code is currently riddled with TODO notes-to-self, old QBASIC code, and unreviewed (and in some cases, intentionally sub-optimal) code structure.  The philosophy behind this project is largely "port the game to Python, test some stuff, and get a few things working, at the expense of writing beautiful code".  Read at your own risk :-D.

### About the Engine
The engine for this game is based on the [Falldown x64 engine](https://github.com/masskonfuzion/falldown_low_rez).  The crowning achievement in the engine programming for this Trick Biker prototype is in breaking the engine code out of Falldown x64, into its own library, and adding some 3D math & perspective code.  The 3D engine is modeled after OpenGL's stack-based matrix framework and graphics pipeline (but of course, OpenGL is leaps and bounds -- and somersaults and Olympic high jumps -- better than my little engine.  The engine code isn't included in this repository (it is written as an external library and imported into this project).  I'm debating whether I should put it in another repository...

## What It Looks Like
Anyway, enough talking.. let's see a video! (Image links to a YouTube video)
[![Trick Biker super-rough prototype](http://img.youtube.com/vi/MbPn-mCCfcQ/hqdefault.jpg)](https://youtu.be/MbPn-mCCfcQ)
