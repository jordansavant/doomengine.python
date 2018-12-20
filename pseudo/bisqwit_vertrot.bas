' Vertex rotation test

SCREEN 7

' The end coordinates for the line segment representing a "wall"
vx1 = 70 : vy1 = 20
vx2 = 70 : vy2 = 70

' The coordinates of the player
px = 50
py = 50
angle = 0

DO
  ' Draw the absolute map
  VIEW(4,40)-(103,149),0,1

  LINE(vx1,vy1)-(vx2,vy2),14
  LINE(px,py)-(COS(angle)*5 + px, SIN(angle)*5 + py),8
  PSET(px,py),15

  ' Draw the transformed map
  VIEW(109,40)-(208,149),0,2

  ' Transform the vertexes relative to the player
  tx1 = vx1 - px : ty1 = vy1 - py
  tx2 = vx2 - px : ty2 = vy2 - py
  ' Rotate them around the player's view
  tz1 = tx1 * COS(angle) + ty1 * SIN(angle)
  tz2 = tx2 * COS(angle) + ty2 * SIN(angle)
  tx1 = tx1 * SIN(angle) - ty1 * COS(angle)
  tx2 = tx2 * SIN(angle) - ty2 * COS(angle)

  LINE(50 - tx1, 50 - tz1) - (50 - tx2, 50 - tz2), 14
  LINE(50,50)-(50,45),8
  PSET(50,50),15
        
  ' Draw the perspective-transformed map
  VIEW(214,40)-(315,149),0,3

  IF tz1 > 0 OR tz2 > 0 THEN
    ' If the line crosses the player's viewplane, clip it.
    CALL Intersect(tx1,tz1, tx2,tz2, -0.0001,0.0001, -20,5, ix1,iz1)
    CALL Intersect(tx1,tz1, tx2,tz2,  0.0001,0.0001,  20,5, ix2,iz2)
    IF tz1 <= 0 THEN IF iz1 > 0 THEN tx1=ix1:tz1=iz1 ELSE tx1=ix2:tz1=iz2
    IF tz2 <= 0 THEN IF iz1 > 0 THEN tx2=ix1:tz2=iz1 ELSE tx2=ix2:tz2=iz2

    x1 = -tx1 * 16 / tz1 : y1a = -50 / tz1 : y1b =  50 / tz1
    x2 = -tx2 * 16 / tz2 : y2a = -50 / tz2 : y2b =  50 / tz2

    LINE(50+x1,50+y1a)-(50+x2,50+y2a),14 'top (1-2 b)
    LINE(50+x1,50+y1b)-(50+x2,50+y2b),14 'bottom (1-2 b)
    LINE(50+x1,50+y1a)-(50+x1,50+y1b),6 'left (1)
    LINE(50+x2,50+y2a)-(50+x2,50+y2b),6 'right (2)
  END IF

  ' Wait for screen refresh and swap page
  SCREEN ,, page%, 1 - page% : page% = 1 - page%
  WAIT &H3DA, &H8, &H8: WAIT &H3DA, &H8

  SELECT CASE INKEY$
    CASE CHR$(0) + "H" : px = px + COS(angle): py = py + SIN(angle)
    CASE CHR$(0) + "P" : px = px - COS(angle): py = py - SIN(angle)
    CASE CHR$(0) + "K": angle = angle - 0.1
    CASE CHR$(0) + "M": angle = angle + 0.1
    CASE "a", "A" : px = px + SIN(angle): py = py - COS(angle)
    CASE "d", "D" : px = px - SIN(angle): py = py + COS(angle)
    CASE "q", "Q", CHR$(27): EXIT DO
  END SELECT
LOOP

SCREEN 0,1,0,0: WIDTH 80,25


DEF FNcross(x1,y1, x2,y2) = x1*y2 - y1*x2

SUB Intersect(x1,y1, x2,y2, x3,y3, x4,y4, x,y)
  x = FNcross(x1,y1, x2,y2)
  y = FNcross(x3,y3, x4,y4)
  det = FNcross(x1-x2, y1-y2, x3-x4, y3-y4)
  x = FNcross(x, x1-x2, y, x3-x4) / det
  y = FNcross(x, y1-y2, y, y3-y4) / det
END SUB


