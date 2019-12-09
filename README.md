# Doom Engine (Renderer) in Python

## Built with
- Python 3.7.1
- pygame, numpy, opengl

In awe of the 1993 doom engine rendering logic regarding Binary Space Partitioning I explored its concepts using a recreation of this engine in Python using pygame as the display portion. The result was great respect for Id Software's work they accomplished.

![](https://github.com/jordansavant/doomengine.python/raw/master/resources/demo_pygame_render.gif)

## How it works:

### The Binary Space Partition
- Two connected vertices define a LineDef
- A LineDef has an outward face to define which side of it is considered open and which side is solid
- A list of LineDefs form a Polygon that can define the boundaries of a room, or "sector"
- A Binary Space Partition class accepts the worlds list of LineDefs
  - The BSP chooses a best candidate "splitter" LineDef by which to judge all other LineDefs
  - The BSP creates two child BSPs to place other LineDefs behind or in front of the splitter
  - LineDefs that cross the plane of the splitter and split into smaller LineDefs to be sorted
- The BSP sorts all LineDefs recursively in the child trees
- Using the BSP we can test whether a position is in open space with a depth search
- Using the BSP we can also render all walls from either back to front or front to back
  - Doom rendered them front to back and used culling to prevent overdraw
  - Other engines have rendered back to front called the Painters Algorithm
- The BSP Tree is built before the game begins as a means of significant performance gain

### The 3D Projection

In DOOM the world, walls and its occupants all live within a 2D plane essentially on an X,Y coordinate system. So at any point the player is surrounded by 2d lines and points that represent walls and enemies.

When it comes time to render the walls in classic DOOM it would traverse its Binary Space Partition testing each wall's 2d start and end positions against the player's 2d position. If the wall was facing the player it would be put in a list. After the traversal this list of walls would be the only walls that needed to be rendered to the screen, all others would be culled.

In fact this list of walls could be further culled because though they all "face" the player, they may not be within the viewport of the camera, such as if they were behind DOOM guy.

Interestingly enough, the order of traversal in the BSP could produce the list in two ways: if the tree was depth-first searched it would produce a list of walls that were sorted by closest to furthest, and if searched oppositely, ie testing at the roots it would produce a list of walls that were sorted furthest to closest.

The order of the resultant list could allow you to render them with the classic "Painter's Algorithm" or inversely how DOOM decided to to it. The Painter's algorithm basically involves rendering the further walls first so that nearby walls get "painted" on top of other walls to produce the correct layering of walls. This was a bit wasteful so in the DOOM engine they rendered in reverse.

Roughly, the DOOM method rendered closest to furthest. It would inspect the closest wall and would run a hardcoded *_3D_* projection matrix against the wall's position at every horizontal pixel on the screen. This would produce a number of vertical pixels (colored and textured) to render at that horizontal pixel position. From there it would test the next wall and if it produced a horizontal position of pixels that overlapped a prior wall's calculation it could be culled.

### Pass 1

I am not an expert on 3D or Linear Algebra so at first I relied heavily on resources listed below to get it "right". In DOOM 

The world is defined in 2D space. Each of the LineDefs as well can have a height property.

The Field of View is hard coded into the matrix mathematics to project the 2D wall into the camera.

I leaned a lot on

![](https://github.com/jordansavant/doomengine.python/raw/master/resources/demo_pygame_render.gif)

*initial engine written purely in pygame worked but had a lot of projection issues*

## Installation

- Install python 3
- Install pygame `pip install -U pygame --user`

## Resources
- Bisqwit Tut: https://bisqwit.iki.fi/jutut/kuvat/programming_examples/portalrendering.html
- BSP Tut: https://www.cs.utah.edu/~jsnider/SeniorProj/BSP1/default.html
- CS Resources: http://www.flipcode.com
- Vector Maths: http://math.hws.edu/graphicsbook/c3/s5.html
- Wolfenstein: https://lodev.org/cgtutor/raycasting.html
