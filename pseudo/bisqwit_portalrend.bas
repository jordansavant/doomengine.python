DEFINT A-Z
REM Portal rendering.
REM
REM ***************************************************************
REM ** This is the first version of my portal rendering program. **
REM ** This is what I planned on featuring in my video,          **
REM ** until I decided to turn it into a C program instead.      **
REM ***************************************************************
REM Copyright (C) 2015 Joel Yliluoma - http://iki.fi/bisqwit/
REM

CLEAR ,,8192

DEFSNG A-Z

' Returns 0 if on line, negative for left, positive for right
DEF FNib(a0,a1,b0,b1) = (a0 < b1) AND (a1 > b0)
DEF FNmin(a,b)
  IF a<b THEN FNmin = a ELSE FNmin = b
END DEF
DEF FNmax(a,b)
  IF a>b THEN FNmax = a ELSE FNmax = b
END DEF
DEF FNintersectBox%(x0,y0, x1,y1, x2,y2, x3,y3) = FNib(FNmin(x0,x1),FNmax(x0,x1),FNmin(x2,x3),FNmax(x2,x3)) _
                                              AND FNib(FNmin(y0,y1),FNmax(y0,y1),FNmin(y2,y3),FNmax(y2,y3))
DEF FNpointSide%(px,py, x0,y0, x1,y1) = SGN( (x1-x0) * (py-y0) - (y1-y0)*(px-x0))

DEFINT A-Z

DEF FNclamp(value, min,max)
  SELECT CASE value
    CASE IS < min: FNclamp = min
    CASE IS > max: FNclamp = max
    CASE ELSE: FNclamp = value
  END SELECT
END DEF


CONST W = 320, H = 240

REM Vertexes: x and y
TYPE xy
  x AS SINGLE
  y AS SINGLE
END TYPE
DIM SHARED vertex(0 TO 99) AS xy

REM Sectors: floor and ceiling height; list of wall vertexes and neighbors
TYPE sector
  floor      AS INTEGER
  ceil       AS INTEGER
  firstpoint AS INTEGER ' index into both points() and neighbors()
  npoints    AS INTEGER
END TYPE
DIM SHARED points(0 TO 199) AS INTEGER, neighbors(0 TO 199) AS INTEGER
DIM SHARED sectors(0 TO 39) AS sector

REM Player: location
TYPE xyz
  x AS SINGLE
  y AS SINGLE
  z AS SINGLE
END TYPE
TYPE player
  where    AS xyz      'Current position
  velocity AS xyz      'Current motion vector
  angle    AS SINGLE   'Looking towards
  anglesin AS SINGLE   'SIN(angle)
  anglecos AS SINGLE   'COS(angle)
  sector   AS INTEGER  'Which sector the player is current in
END TYPE
DIM SHARED player AS player

CALL ReadData

SCREEN 13

DIM SHARED ytop(0 TO W-1), ybottom(0 TO W-1), renderedsectors(0 TO 39)

DO
  DrawScreen
  LOCATE 1,1: PRINT player.where.x;player.where.y;player.sector
  
reinkeys:
  SELECT CASE INKEY$
    CASE CHR$(0) + "H" : moveplayer player.anglecos* 0.3, player.anglesin* 0.3, 0
    CASE CHR$(0) + "P" : moveplayer player.anglecos*-0.3, player.anglesin*-0.3, 0
    CASE "a"           : moveplayer player.anglesin* 0.3, player.anglecos*-0.3, 0
    CASE "d"           : moveplayer player.anglesin*-0.3, player.anglecos* 0.3, 0
    CASE CHR$(0) + "K": player.angle = player.angle - 0.1
    CASE CHR$(0) + "M": player.angle = player.angle + 0.1
    CASE "q","Q",CHR$(27): EXIT DO
    CASE "": SLEEP 1:GOTO reinkeys
  END SELECT
  player.anglesin = SIN(player.angle)
  player.anglecos = COS(player.angle)
LOOP

END

REM Vertexes (Y coordinate, followed by list of X coordinates terminated by "x"):
DATA 0,   0,16,x
DATA 1,   1,3,20,22,x
DATA 3,   3,9,17.5,20,x
DATA 3.5, 9,17.5,x
DATA 4,   8,13,16,x
DATA 4.9, 13,16,x
DATA 5,   4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,x
DATA 9,   4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,x
DATA 9.1, 13,16,x
DATA 10,  8,13,16,x
DATA 10.5,9,17.5,x
DATA 11,  3,9,17.5,20,x
DATA 13,  1,3,20,22,x
DATA 14,  0,16,x,*
REM Sectors (floor height, ceiling height, then vertex numbers in clockwise order, terminated by "x")
REM After the list of vertexes, comes the list of sector numbers on the "opposite" side of that wall; "x" = none.
DATA  0,20, 1,14,13,12,0, x,         x,x,5,x,1
DATA  0,20, 12,17,0,x,               0,8,2
DATA  0,20, 17,34,66,0, x,           1,10,3,x
DATA  0,20, 34,53,66,x,              2,9,4
DATA  0,20, 54,55,67,66,53, x,       x,6,x,x,3
DATA  0,12, 14,16,15,13, x,          0,x,7,x
DATA  0,12, 52,55,54,51, x,          7,x,4,x
DATA  0,12, 16,52,51,15, x,          5,x,6,x
DATA  0,20, 12,21,20,19,18,17, x,    1,x,13,12,11,10
DATA  0,20, 35,36,37,38,53,34, x,    10,11,12,13,x,3
DATA  1,20, 17,18,35,34, x,          2,8,11,9
DATA  2,20, 18,19,36,35, x,          10,8,12,9
DATA  3,20, 19,20,37,36, x,          11,8,13,9
DATA  4,20, 20,21,38,37, x,          12,8,14,9
DATA  5,20, 21,22,39,38, x,          13,x,15,x
DATA  6,20, 22,23,40,39, x,          14,x,16,x
DATA  7,20, 23,24,41,40, x,          15,x,17,x
DATA  8,24, 24,25,42,41, x,          16,x,18,x
DATA  9,24, 25,26,43,42, x,          17,x,19,x
DATA 10,24, 26,27,44,43, x,          18,x,20,x
DATA 11,24, 27,28,45,44, x,          19,x,21,x
DATA 12,28, 28,29,46,45, x,          20,x,22,x
DATA 13,28, 29,30,47,46, x,          21,x,23,x
DATA 14,28, 30,31,48,47, x,          22,x,24,x
DATA 15,28, 31,32,49,48, x,          23,x,25,x
DATA 16,28, 32,33,50,49, x,          24,x,26,x
DATA 16,28, 5,65,64,61,50,33,9,4, x, x,x,x,28,x,25,x,27 
DATA 16,28, 4,9,8,7,6,3, x,          x,26,x,30,x,29
DATA 16,28, 59,60,61,64,63,58, x,    x,31,x,26,x,29
DATA 16,28, 3,6,58,63,62,2, x,       x,27,x,28,x,x
DATA 17,27, 8,11,10,7, x,            27,x,32,x
DATA 17,27, 57,60,59,56, x,          32,x,28,x
DATA 18,26, 11,57,56,10, x,          30,x,31,x, *
REM Player: Location (x,y), angle, and sector number
DATA 1,7, 0, 2

DIM SHARED r$
DEF FNREAD$
  READ r$
  FNREAD$ = r$
END DEF

SUB ReadData
  REM Read vertexes
  n = 0
  WHILE FNREAD$ <> "*"
    y = VAL(r$)
    WHILE FNREAD$ <> "x"
      vertex(n).y = y
      vertex(n).x = VAL(r$)
      n = n + 1
    WEND
  WEND
  REM Read sectors
  n = 0: p = 0
  WHILE FNREAD$ <> "*"
    y = VAL(r$)
    sectors(n).firstpoint = p
    sectors(n).floor = y
    sectors(n).ceil  = VAL(FNREAD$)
    np = 0
    WHILE FNREAD$ <> "x"
      points(p + np) = VAL(r$)
      np = np + 1
    WEND
    sectors(n).npoints = np
    FOR x = 0 TO np-1
      IF FNREAD$ = "x" THEN y = -1 ELSE y = VAL(r$)
      neighbors(p + x) = y
    NEXT
    p = p + np
    n = n + 1
  WEND
  READ player.where.x, player.where.y, player.angle, player.sector
  player.where.z = sectors( player.sector ).floor + 5
  
  player.anglesin = SIN(player.angle)
  player.anglecos = COS(player.angle)
END SUB

SUB DrawScreen
  FOR x=0 TO W-1 : ytop(x)    =   0: NEXT
  FOR x=0 TO W-1 : ybottom(x) = H-1: NEXT
  RenderSector player.sector, 0, W-1
END SUB

SUB moveplayer(dx AS SINGLE, dy AS SINGLE, dz AS SINGLE)
  DIM ox AS SINGLE, oy AS SINGLE, nx AS SINGLE, ny AS SINGLE
  DIM vx1 AS SINGLE, vy1 AS SINGLE, vx2 AS SINGLE, vy2 AS SINGLE

  ox = player.where.x
  oy = player.where.y
  nx = player.where.x + dx
  ny = player.where.y + dy
  
  ' Check if this movement crosses one of this sector's walls.
  sectorno = player.sector
  v2 = points(sectors(sectorno).firstpoint + sectors(sectorno).npoints - 1)
  FOR s = 1 TO sectors(sectorno).npoints
    p = sectors(sectorno).firstpoint + s - 1
    ' v1,v2 = the two vertex numbers of this edge of the sector
    v1 = v2
    v2 = points(p)
    ' If there is anything on the other side of this wall...
    IF neighbors(p) >= 0 THEN
      ' Acquire the x,y coordinates of these two vertexes
      vx1 = vertex(v1).x : vy1 = vertex(v1).y
      vx2 = vertex(v2).x : vy2 = vertex(v2).y
      IF FNintersectBox%(ox,oy, nx,ny, vx1,vy1, vx2,vy2) THEN
        oldside = FNpointSide%(ox,oy, vx1,vy1,vx2,vy2)
        newside = FNpointSide%(nx,ny, vx1,vy1,vx2,vy2)
        IF oldside <> newside AND newside <> 0 THEN
          player.sector = neighbors(p)
          EXIT FOR
        END IF
      END IF
    END IF
  NEXT
  player.where.x = nx
  player.where.y = ny
  player.where.z = sectors(player.sector).floor + 4 'player.where.z + dz
END SUB

SUB RenderSector(sectorno, sx1,sx2)
  DIM vx1 AS SINGLE, vy1 AS SINGLE, vx2 AS SINGLE, vy2 AS SINGLE
  DIM yceil AS SINGLE, yfloor AS SINGLE
  DIM tz1 AS SINGLE, tz2 AS SINGLE, tx1 AS SINGLE, tx2 AS SINGLE
  DIM xscale1 AS SINGLE, yscale1 AS SINGLE, xscale2 AS SINGLE, yscale2 AS SINGLE
  DIM ya AS LONG, yb AS LONG, nya AS LONG, nyb AS LONG
  
  IF renderedsectors%(sectorno) THEN EXIT SUB
  renderedsectors%(sectorno) = 1

  ' Render each wall of this sector that is facing towards player.
  v2 = points(sectors(sectorno).firstpoint + sectors(sectorno).npoints - 1)
  
  FOR s = 1 TO sectors(sectorno).npoints
    p = sectors(sectorno).firstpoint + s - 1
    ' v1,v2 = the two vertex numbers of this edge of the sector
    v1 = v2
    v2 = points(p)
    ' Acquire the x,y coordinates of these two vertexes
    vx1 = vertex(v1).x : vy1 = vertex(v1).y
    vx2 = vertex(v2).x : vy2 = vertex(v2).y
    ' Transform the vertices into the player's view
    vx1 = vx1 - player.where.x : vy1 = vy1 - player.where.y
    vx2 = vx2 - player.where.x : vy2 = vy2 - player.where.y
    ' Rotate them around the player's view
    tz1 = vx1 * player.anglecos + vy1 * player.anglesin
    tz2 = vx2 * player.anglecos + vy2 * player.anglesin
    ' Is the wall at least partially in front of the player?
    IF tz1 <= 0 AND tz2 <= 0 THEN GOTO nextsector
    ' Yes (either Z was > 0). Do the rest of the rotation
    tx1 = vx1 * player.anglesin - vy1 * player.anglecos
    tx2 = vx2 * player.anglesin - vy2 * player.anglecos
    ' If it's partially behind the player, clip it at z=0.1
    IF tz1 <= 0 THEN tx1 = (0.1-tz1)*(tx2-tx1)/(tz2-tz1)+tx1 : tz1 = 0.1
    IF tz2 <= 0 THEN tx2 = (0.1-tz2)*(tx1-tx2)/(tz1-tz2)+tx2 : tz2 = 0.1
    ' Do perspective transformation
    xscale1 = 140 / tz1: yscale1 = 32 / tz1
    xscale2 = 140 / tz2: yscale2 = 32 / tz2
    x1 = W\2 + CINT(-tx1 * xscale1)
    x2 = W\2 + CINT(-tx2 * xscale2)
    IF x1 = x2 THEN GOTO nextsector
    ' Acquire and transform the floor and ceiling heights
    yceil  = sectors(sectorno).ceil  - player.where.z
    yfloor = sectors(sectorno).floor - player.where.z
    y1a = H\2 + CINT( -yceil * yscale1): y1b = H\2 + CINT( -yfloor * yscale1)
    y2a = H\2 + CINT( -yceil * yscale2): y2b = H\2 + CINT( -yfloor * yscale2)
    ' Clip to the horizontally visible region.
    beginx = sx1 : IF beginx < x1 THEN beginx = x1
    endx   = sx2 : IF endx   > x2 THEN endx   = x2
    ' Check what kind of view we have.
    neighbor = neighbors(p)
    IF neighbor >= 0 THEN
      ' Something is showing through this wall (portal).
      ' Perspective-transform the floor and ceiling coordinates of the neighboring sector.
      nyceil  = sectors(neighbor).ceil  - player.where.z
      nyfloor = sectors(neighbor).floor - player.where.z
      ny1a = H\2 + CINT( -nyceil * yscale1): ny1b = H\2 + CINT( -nyfloor * yscale1)
      ny2a = H\2 + CINT( -nyceil * yscale2): ny2b = H\2 + CINT( -nyfloor * yscale2)
    END IF
    ' Just the wall.
    FOR x = beginx TO endx
      ' Acquire the Y coordinates for our floor & ceiling for this X coordinate
      ya = (x-x1) * CLNG(y2a-y1a) \ (x2-x1) + y1a
      yb = (x-x1) * CLNG(y2b-y1b) \ (x2-x1) + y1b
      ' Clamp the ya & yb
      cya = FNclamp(ya, ytop%(x),ybottom%(x))
      cyb = FNclamp(yb, ytop%(x),ybottom%(x))
      ' Render ceiling: everything above this sector's ceiling height.
      vline x, ytop%(x), cya, 17,18,17
      ' Render floor: everything below this sector's floor height.
      vline x, cyb, ybottom%(x), 32,1,32
      ' Render wall (if there's a wall).
      IF neighbor < 0 THEN
        e% = 7: IF x = x1 OR x = x2 THEN e% = 0
        vline x, cya+1, cyb-1, 0,e%,0
      ELSE
        ' Same for _their_ floor and ceiling
        nya = (x-x1) * CLNG(ny2a-ny1a) \ (x2-x1) + ny1a
        nyb = (x-x1) * CLNG(ny2b-ny1b) \ (x2-x1) + ny1b
        ' Clamp ya2 and yb2
        cnya = FNclamp(nya, ytop%(x),ybottom%(x))
        cnyb = FNclamp(nyb, ytop%(x),ybottom%(x))

        'If our ceiling is higher than their ceiling, render upper wall
        IF cnya > cya THEN
          e% = 7: IF x = x1 OR x = x2 THEN e% = 0
          vline x, cya+1, cnya, 0,e%,0
          ytop%(x) = FNclamp(cnya + 1, ytop%(x),199)
        ELSE
          ytop%(x) = FNclamp(cya + 1, ytop%(x),199)
        END IF
        'If our floor is lower than their floor, render bottom wall
        IF cyb > cnyb THEN
          e% = 34: IF x = x1 OR x = x2 THEN e% = 0
          vline x, cnyb, cyb-1, 0,e%,0
          ybottom%(x) = FNclamp(cnyb - 1, 0,ybottom%(x))
        ELSE
          ybottom%(x) = FNclamp(cyb - 1, 0,ybottom%(x))
        END IF
        
        'vline x, ytop%(x),ybottom%(x), 5,5,5
      END IF
    NEXT
    ' Render that other sector now in the window formed by this wall.
    IF neighbor >= 0 AND endx >= beginx THEN RenderSector neighbor, beginx,endx
nextsector:
  NEXT
  renderedsectors%(sectorno) = 0
END SUB

SUB vline(x, y1,y2, top,middle,bottom)
  IF y1 < 0 THEN y1 = 0 ELSE IF y1 > 199 THEN y1 = 199
  IF y2 < 0 THEN y2 = 0 ELSE IF y2 > 199 THEN y2 = 199
  IF y2 < y1 THEN EXIT SUB
  
  IF y2 = y1 THEN
    PSET(x,y1),middle
  ELSE
    PSET(x,y1),top
    LINE(x,y1+1)-(x,y2-1),middle
    PSET(x,y2),bottom
  END IF
END SUB