#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <SDL.h>

/* Define window size */
#define W 608
#define H 480
/* Define various vision related constants */
#define EyeHeight  6    // Camera height from floor when standing
#define DuckHeight 2.5  // And when crouching
#define HeadMargin 1    // How much room there is above camera before the head hits the ceiling
#define KneeHeight 2    // How tall obstacles the player can simply walk over without jumping
#define hfov (0.73f*H)  // Affects the horizontal field of vision
#define vfov (.2f*H)    // Affects the vertical field of vision

/* Sectors: Floor and ceiling height; list of edge vertices and neighbors */
static struct sector
{
    float floor, ceil;
    struct xy { float x,y; } *vertex; // Each vertex has an x and y coordinate
    signed char *neighbors;           // Each edge may have a corresponding neighboring sector
    unsigned npoints;                 // How many vertexes there are
} *sectors = NULL;
static unsigned NumSectors = 0;

/* Player: location */
static struct player
{
    struct xyz { float x,y,z; } where,      // Current position
                                velocity;   // Current motion vector
    float angle, anglesin, anglecos, yaw;   // Looking towards (and sin() and cos() thereof)
    unsigned sector;                        // Which sector the player is currently in
} player;

// Utility functions. Because C doesn't have templates,
// we use the slightly less safe preprocessor macros to
// implement these functions that work with multiple types.
#define min(a,b)             (((a) < (b)) ? (a) : (b)) // min: Choose smaller of two scalars.
#define max(a,b)             (((a) > (b)) ? (a) : (b)) // max: Choose greater of two scalars.
#define clamp(a, mi,ma)      min(max(a,mi),ma)         // clamp: Clamp value into set range.
#define vxs(x0,y0, x1,y1)    ((x0)*(y1) - (x1)*(y0))   // vxs: Vector cross product
// Overlap:  Determine whether the two number ranges overlap.
#define Overlap(a0,a1,b0,b1) (min(a0,a1) <= max(b0,b1) && min(b0,b1) <= max(a0,a1))
// IntersectBox: Determine whether two 2D-boxes intersect.
#define IntersectBox(x0,y0, x1,y1, x2,y2, x3,y3) (Overlap(x0,x1,x2,x3) && Overlap(y0,y1,y2,y3))
// PointSide: Determine which side of a line the point is on. Return value: <0, =0 or >0.
#define PointSide(px,py, x0,y0, x1,y1) vxs((x1)-(x0), (y1)-(y0), (px)-(x0), (py)-(y0))
// Intersect: Calculate the point of intersection between two lines.
#define Intersect(x1,y1, x2,y2, x3,y3, x4,y4) ((struct xy) { \
    vxs(vxs(x1,y1, x2,y2), (x1)-(x2), vxs(x3,y3, x4,y4), (x3)-(x4)) / vxs((x1)-(x2), (y1)-(y2), (x3)-(x4), (y3)-(y4)), \
    vxs(vxs(x1,y1, x2,y2), (y1)-(y2), vxs(x3,y3, x4,y4), (y3)-(y4)) / vxs((x1)-(x2), (y1)-(y2), (x3)-(x4), (y3)-(y4)) })

static void LoadData()
{
    FILE* fp = fopen("map-clear.txt", "rt");
    if(!fp) { perror("map-clear.txt"); exit(1); }
    char Buf[256], word[256], *ptr;
    struct xy* vert = NULL, v;
    int n, m, NumVertices = 0;
    while(fgets(Buf, sizeof Buf, fp))
        switch(sscanf(ptr = Buf, "%32s%n", word, &n) == 1 ? word[0] : '\0')
        {
            case 'v': // vertex
                for(sscanf(ptr += n, "%f%n", &v.y, &n); sscanf(ptr += n, "%f%n", &v.x, &n) == 1; )
                    { vert = realloc(vert, ++NumVertices * sizeof(*vert)); vert[NumVertices-1] = v; }
                break;
            case 's': // sector
                sectors = realloc(sectors, ++NumSectors * sizeof(*sectors));
                struct sector* sect = &sectors[NumSectors-1];
                int* num = NULL;
                sscanf(ptr += n, "%f%f%n", &sect->floor,&sect->ceil, &n);
                for(m=0; sscanf(ptr += n, "%32s%n", word, &n) == 1 && word[0] != '#'; )
                    { num = realloc(num, ++m * sizeof(*num)); num[m-1] = word[0]=='x' ? -1 : atoi(word); }
                sect->npoints   = m /= 2;
                sect->neighbors = malloc( (m  ) * sizeof(*sect->neighbors) );
                sect->vertex    = malloc( (m+1) * sizeof(*sect->vertex)    );
                for(n=0; n<m; ++n) sect->neighbors[n] = num[m + n];
                for(n=0; n<m; ++n) sect->vertex[n+1]  = vert[num[n]]; // TODO: Range checking
                sect->vertex[0] = sect->vertex[m]; // Ensure the vertexes form a loop
                free(num);
                break;
            case 'p':; // player
                float angle;
                sscanf(ptr += n, "%f %f %f %d", &v.x, &v.y, &angle,&n);
                player = (struct player) { {v.x, v.y, 0}, {0,0,0}, angle,0,0,0, n }; // TODO: Range checking
                player.where.z = sectors[player.sector].floor + EyeHeight;
        }
    fclose(fp);
    free(vert);
}
static void UnloadData()
{
    for(unsigned a=0; a<NumSectors; ++a) free(sectors[a].vertex);
    for(unsigned a=0; a<NumSectors; ++a) free(sectors[a].neighbors);
    free(sectors);
    sectors    = NULL;
    NumSectors = 0;
}

static SDL_Surface* surface = NULL;

/* vline: Draw a vertical line on screen, with a different color pixel in top & bottom */
static void vline(int x, int y1,int y2, int top,int middle,int bottom)
{
    int *pix = (int*) surface->pixels;
    y1 = clamp(y1, 0, H-1);
    y2 = clamp(y2, 0, H-1);
    if(y2 == y1)
        pix[y1*W+x] = middle;
    else if(y2 > y1)
    {
        pix[y1*W+x] = top;
        for(int y=y1+1; y<y2; ++y) pix[y*W+x] = middle;
        pix[y2*W+x] = bottom;
    }
}

/* MovePlayer(dx,dy): Moves the player by (dx,dy) in the map, and
 * also updates their anglesin/anglecos/sector properties properly.
 */
static void MovePlayer(float dx, float dy)
{
    float px = player.where.x, py = player.where.y;
    /* Check if this movement crosses one of this sector's edges
     * that have a neighboring sector on the other side.
     * Because the edge vertices of each sector are defined in
     * clockwise order, PointSide will always return -1 for a point
     * that is outside the sector and 0 or 1 for a point that is inside.
     */
    const struct sector* const sect = &sectors[player.sector];
    const struct xy* const vert = sect->vertex;
    for(unsigned s = 0; s < sect->npoints; ++s)
        if(sect->neighbors[s] >= 0
        && IntersectBox(px,py, px+dx,py+dy, vert[s+0].x, vert[s+0].y, vert[s+1].x, vert[s+1].y)
        && PointSide(px+dx, py+dy, vert[s+0].x, vert[s+0].y, vert[s+1].x, vert[s+1].y) < 0)
        {
            player.sector = sect->neighbors[s];
            break;
        }

    player.where.x += dx;
    player.where.y += dy;
    player.anglesin = sinf(player.angle);
    player.anglecos = cosf(player.angle);
}

static void DrawScreen()
{
    enum { MaxQueue = 32 };  // maximum number of pending portal renders
    struct item { int sectorno,sx1,sx2; } queue[MaxQueue], *head=queue, *tail=queue;
    int ytop[W]={0}, ybottom[W], renderedsectors[NumSectors];
    for(unsigned x=0; x<W; ++x) ybottom[x] = H-1;
    for(unsigned n=0; n<NumSectors; ++n) renderedsectors[n] = 0;

    /* Begin whole-screen rendering from where the player is. */
    *head = (struct item) { player.sector, 0, W-1 };
    if(++head == queue+MaxQueue) head = queue;

    do {
    /* Pick a sector & slice from the queue to draw */
    const struct item now = *tail;
    if(++tail == queue+MaxQueue) tail = queue;

    if(renderedsectors[now.sectorno] & 0x21) continue; // Odd = still rendering, 0x20 = give up
    ++renderedsectors[now.sectorno];
    const struct sector* const sect = &sectors[now.sectorno];
    /* Render each wall of this sector that is facing towards player. */
    for(unsigned s = 0; s < sect->npoints; ++s)
    {
        /* Acquire the x,y coordinates of the two endpoints (vertices) of this edge of the sector */
        float vx1 = sect->vertex[s+0].x - player.where.x, vy1 = sect->vertex[s+0].y - player.where.y;
        float vx2 = sect->vertex[s+1].x - player.where.x, vy2 = sect->vertex[s+1].y - player.where.y;
        /* Rotate them around the player's view */
        float pcos = player.anglecos, psin = player.anglesin;
        float tx1 = vx1 * psin - vy1 * pcos,  tz1 = vx1 * pcos + vy1 * psin;
        float tx2 = vx2 * psin - vy2 * pcos,  tz2 = vx2 * pcos + vy2 * psin;
        /* Is the wall at least partially in front of the player? */
        if(tz1 <= 0 && tz2 <= 0) continue;
        /* If it's partially behind the player, clip it against player's view frustrum */
        if(tz1 <= 0 || tz2 <= 0)
        {
            float nearz = 1e-4f, farz = 5, nearside = 1e-5f, farside = 20.f;
            // Find an intersection between the wall and the approximate edges of player's view
            struct xy i1 = Intersect(tx1,tz1,tx2,tz2, -nearside,nearz, -farside,farz);
            struct xy i2 = Intersect(tx1,tz1,tx2,tz2,  nearside,nearz,  farside,farz);
            if(tz1 < nearz) { if(i1.y > 0) { tx1 = i1.x; tz1 = i1.y; } else { tx1 = i2.x; tz1 = i2.y; } }
            if(tz2 < nearz) { if(i1.y > 0) { tx2 = i1.x; tz2 = i1.y; } else { tx2 = i2.x; tz2 = i2.y; } }
        }
        /* Do perspective transformation */
        float xscale1 = hfov / tz1, yscale1 = vfov / tz1;    int x1 = W/2 - (int)(tx1 * xscale1);
        float xscale2 = hfov / tz2, yscale2 = vfov / tz2;    int x2 = W/2 - (int)(tx2 * xscale2);
        if(x1 >= x2 || x2 < now.sx1 || x1 > now.sx2) continue; // Only render if it's visible
        /* Acquire the floor and ceiling heights, relative to where the player's view is */
        float yceil  = sect->ceil  - player.where.z;
        float yfloor = sect->floor - player.where.z;
        /* Check the edge type. neighbor=-1 means wall, other=boundary between two sectors. */
        int neighbor = sect->neighbors[s];
        float nyceil=0, nyfloor=0;
        if(neighbor >= 0) // Is another sector showing through this portal?
        {
            nyceil  = sectors[neighbor].ceil  - player.where.z;
            nyfloor = sectors[neighbor].floor - player.where.z;
        }
        /* Project our ceiling & floor heights into screen coordinates (Y coordinate) */
        #define Yaw(y,z) (y + z*player.yaw)
        int y1a  = H/2 - (int)(Yaw(yceil, tz1) * yscale1),  y1b = H/2 - (int)(Yaw(yfloor, tz1) * yscale1);
        int y2a  = H/2 - (int)(Yaw(yceil, tz2) * yscale2),  y2b = H/2 - (int)(Yaw(yfloor, tz2) * yscale2);
        /* The same for the neighboring sector */
        int ny1a = H/2 - (int)(Yaw(nyceil, tz1) * yscale1), ny1b = H/2 - (int)(Yaw(nyfloor, tz1) * yscale1);
        int ny2a = H/2 - (int)(Yaw(nyceil, tz2) * yscale2), ny2b = H/2 - (int)(Yaw(nyfloor, tz2) * yscale2);

        /* Render the wall. */
        int beginx = max(x1, now.sx1), endx = min(x2, now.sx2);
        for(int x = beginx; x <= endx; ++x)
        {
            /* Calculate the Z coordinate for this point. (Only used for lighting.) */
            int z = ((x - x1) * (tz2-tz1) / (x2-x1) + tz1) * 8;
            /* Acquire the Y coordinates for our ceiling & floor for this X coordinate. Clamp them. */
            int ya = (x - x1) * (y2a-y1a) / (x2-x1) + y1a, cya = clamp(ya, ytop[x],ybottom[x]); // top
            int yb = (x - x1) * (y2b-y1b) / (x2-x1) + y1b, cyb = clamp(yb, ytop[x],ybottom[x]); // bottom

            /* Render ceiling: everything above this sector's ceiling height. */
            vline(x, ytop[x], cya-1, 0x111111 ,0x222222,0x111111);
            /* Render floor: everything below this sector's floor height. */
            vline(x, cyb+1, ybottom[x], 0x0000FF,0x0000AA,0x0000FF);

            /* Is there another sector behind this edge? */
            if(neighbor >= 0)
            {
                /* Same for _their_ floor and ceiling */
                int nya = (x - x1) * (ny2a-ny1a) / (x2-x1) + ny1a, cnya = clamp(nya, ytop[x],ybottom[x]);
                int nyb = (x - x1) * (ny2b-ny1b) / (x2-x1) + ny1b, cnyb = clamp(nyb, ytop[x],ybottom[x]);
                /* If our ceiling is higher than their ceiling, render upper wall */
                unsigned r1 = 0x010101 * (255-z), r2 = 0x040007 * (31-z/8);
                vline(x, cya, cnya-1, 0, x==x1||x==x2 ? 0 : r1, 0); // Between our and their ceiling
                ytop[x] = clamp(max(cya, cnya), ytop[x], H-1);   // Shrink the remaining window below these ceilings
                /* If our floor is lower than their floor, render bottom wall */
                vline(x, cnyb+1, cyb, 0, x==x1||x==x2 ? 0 : r2, 0); // Between their and our floor
                ybottom[x] = clamp(min(cyb, cnyb), 0, ybottom[x]); // Shrink the remaining window above these floors
            }
            else
            {
                /* There's no neighbor. Render wall from top (cya = ceiling level) to bottom (cyb = floor level). */
                unsigned r = 0x010101 * (255-z);
                vline(x, cya, cyb, 0, x==x1||x==x2 ? 0 : r, 0);
            }
        }
        /* Schedule the neighboring sector for rendering within the window formed by this wall. */
        if(neighbor >= 0 && endx >= beginx && (head+MaxQueue+1-tail)%MaxQueue)
        {
            *head = (struct item) { neighbor, beginx, endx };
            if(++head == queue+MaxQueue) head = queue;
        }
    } // for s in sector's edges
    ++renderedsectors[now.sectorno];
    } while(head != tail); // render any other queued sectors
}

int main()
{
    LoadData();

    surface = SDL_SetVideoMode(W, H, 32, 0);

    SDL_EnableKeyRepeat(150, 30);
    SDL_ShowCursor(SDL_DISABLE);

    int wsad[4]={0,0,0,0}, ground=0, falling=1, moving=0, ducking=0;
    float yaw = 0;
    for(;;)
    {
        SDL_LockSurface(surface);
        DrawScreen();
        SDL_UnlockSurface(surface);
        SDL_Flip(surface);

        /* Vertical collision detection */
        float eyeheight = ducking ? DuckHeight : EyeHeight;
        ground = !falling;
        if(falling)
        {
            player.velocity.z -= 0.05f; /* Add gravity */
            float nextz = player.where.z + player.velocity.z;
            if(player.velocity.z < 0 && nextz  < sectors[player.sector].floor + eyeheight) // When going down
            {
                /* Fix to ground */
                player.where.z    = sectors[player.sector].floor + eyeheight;
                player.velocity.z = 0;
                falling = 0;
                ground  = 1;
            }
            else if(player.velocity.z > 0 && nextz > sectors[player.sector].ceil) // When going up
            {
                /* Prevent jumping above ceiling */
                player.velocity.z = 0;
                falling = 1;
            }
            if(falling)
            {
                player.where.z += player.velocity.z;
                moving = 1;
            }
        }
        /* Horizontal collision detection */
        if(moving)
        {
            float px = player.where.x,    py = player.where.y;
            float dx = player.velocity.x, dy = player.velocity.y;

            const struct sector* const sect = &sectors[player.sector];
            const struct xy* const vert = sect->vertex;
            /* Check if the player is about to cross one of the sector's edges */
            for(unsigned s = 0; s < sect->npoints; ++s)
                if(IntersectBox(px,py, px+dx,py+dy, vert[s+0].x, vert[s+0].y, vert[s+1].x, vert[s+1].y)
                && PointSide(px+dx, py+dy, vert[s+0].x, vert[s+0].y, vert[s+1].x, vert[s+1].y) < 0)
                {
                    /* Check where the hole is. */
                    float hole_low  = sect->neighbors[s] < 0 ?  9e9 : max(sect->floor, sectors[sect->neighbors[s]].floor);
                    float hole_high = sect->neighbors[s] < 0 ? -9e9 : min(sect->ceil,  sectors[sect->neighbors[s]].ceil );
                    /* Check whether we're bumping into a wall. */
                    if(hole_high < player.where.z+HeadMargin
                    || hole_low  > player.where.z-eyeheight+KneeHeight)
                    {
                        /* Bumps into a wall! Slide along the wall. */
                        /* This formula is from Wikipedia article "vector projection". */
                        float xd = vert[s+1].x - vert[s+0].x, yd = vert[s+1].y - vert[s+0].y;
                        dx = xd * (dx*xd + yd*dy) / (xd*xd + yd*yd);
                        dy = yd * (dx*xd + yd*dy) / (xd*xd + yd*yd);
                        moving = 0;
                    }
                }
            MovePlayer(dx, dy);
            falling = 1;
        }

        SDL_Event ev;
        while(SDL_PollEvent(&ev))
            switch(ev.type)
            {
                case SDL_KEYDOWN:
                case SDL_KEYUP:
                    switch(ev.key.keysym.sym)
                    {
                        case 'w': wsad[0] = ev.type==SDL_KEYDOWN; break;
                        case 's': wsad[1] = ev.type==SDL_KEYDOWN; break;
                        case 'a': wsad[2] = ev.type==SDL_KEYDOWN; break;
                        case 'd': wsad[3] = ev.type==SDL_KEYDOWN; break;
                        case 'q': goto done;
                        case ' ': /* jump */
                            if(ground) { player.velocity.z += 0.5; falling = 1; }
                            break;
                        case SDLK_LCTRL: /* duck */
                        case SDLK_RCTRL: ducking = ev.type==SDL_KEYDOWN; falling=1; break;
                        default: break;
                    }
                    break;
                case SDL_QUIT: goto done;
            }

        /* mouse aiming */
        int x,y;
        SDL_GetRelativeMouseState(&x,&y);
        player.angle += x * 0.03f;
        yaw          = clamp(yaw - y*0.05f, -5, 5);
        player.yaw   = yaw - player.velocity.z*0.5f;
        MovePlayer(0,0);

        float move_vec[2] = {0.f, 0.f};
        if(wsad[0]) { move_vec[0] += player.anglecos*0.2f; move_vec[1] += player.anglesin*0.2f; }
        if(wsad[1]) { move_vec[0] -= player.anglecos*0.2f; move_vec[1] -= player.anglesin*0.2f; }
        if(wsad[2]) { move_vec[0] += player.anglesin*0.2f; move_vec[1] -= player.anglecos*0.2f; }
        if(wsad[3]) { move_vec[0] -= player.anglesin*0.2f; move_vec[1] += player.anglecos*0.2f; }
        int pushing = wsad[0] || wsad[1] || wsad[2] || wsad[3];
        float acceleration = pushing ? 0.4 : 0.2;

        player.velocity.x = player.velocity.x * (1-acceleration) + move_vec[0] * acceleration;
        player.velocity.y = player.velocity.y * (1-acceleration) + move_vec[1] * acceleration;

        if(pushing) moving = 1;

        SDL_Delay(10);
    }
done:
    UnloadData();
    SDL_Quit();
    return 0;
}













































































