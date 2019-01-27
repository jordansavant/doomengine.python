# Doom Engine (Renderer) in Python

In awe of the 1993 doom engine rendering logic regarding Binary Space Partitioning I explored its concepts using a recreation of this engine in Python using pygame as the display portion. The result was great respect for Id Software's work they accomplished.

<img src="https://media.giphy.com/media/PNfObqJPEaHiPRt2zL/giphy.gif" width="500" />

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

I am not an expert on 3D or Linear Algebra so I relied heavily on resources listed below to get it "right"

The world is defined in 2D space. Each of the LineDefs as well can have a height property.

The Field of View is hard coded into the matrix mathematics to project the 2D wall into the camera.

## Installation

- Install python 3
- Install pygame `pip install -U pygame --user`

## Resources
- Bisqwit Tut: https://bisqwit.iki.fi/jutut/kuvat/programming_examples/portalrendering.html
- BSP Tut: https://www.cs.utah.edu/~jsnider/SeniorProj/BSP1/default.html
- CS Resources: http://www.flipcode.com
- Vector Maths: http://math.hws.edu/graphicsbook/c3/s5.html
- Wolfenstein: https://lodev.org/cgtutor/raycasting.html
