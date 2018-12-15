struct NODE 
{
    POLYGON * Splitter;
    NODE * Front;
    NODE * Back;
    BOOL IsLeaf;
    BOOL IsSolid;
};

struct POLYGON 
{
    D3DLVERTEX VertexList[10]; // shape
    D3DVECTOR Normal; // perpendicular "facing" direction ? how does that work with lots of points?
    WORD NumberOfVertices;
    WORD NumberOfIndices;
    WORD Indices[30];
    POLYGON * Next; // used in bsp compiler, linked list from polygon to polygon
};


// Builds some sort of polygons from this aweful structure:
// BYTE BSPMAP []=
// {0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
// 0,0,2,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,
// 0,2,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,
// 1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,0,1,
// 0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,
// 0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,
// 0,1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,3,1,
// 0,2,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,
// 1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,
// 0,1,0,0,0,0,1,2,0,0,0,1,0,0,0,1,0,0,0,1,
// 0,1,0,0,0,1,2,0,0,0,0,1,1,0,0,0,0,0,0,1,
// 0,1,0,0,0,1,0,0,0,0,0,3,1,0,0,0,0,0,0,1,
// 0,1,0,1,1,2,0,0,0,0,0,0,1,0,0,0,0,0,0,1,
// 1,2,0,0,0,0,0,0,1,0,0,0,1,1,1,1,0,0,0,1, 
// 1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
// 1,0,0,1,2,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
// 1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,
// 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1};
//
// { , , ,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
//  , ,2, , , , , , , , ,3, , , , , , , , ,
//  ,2, , , , , , , , , , ,3, , , , , , , ,
// 1, , , , , , , , , , , , ,1,1,1,1,1, ,1,
//  ,1, , , , , , , , , , , , , , , ,1, ,1,
//  ,1, , , , , , , , , , , , , , , ,1,1,1,
//  ,1,1, , , , ,1, , , , , , , , , , ,3,1,
//  ,2, , , , , ,1, , , , , , , ,1, , , ,1,
// 1, , , , , , ,1, , , , , , , ,1, , , ,1,
//  ,1, , , , ,1,2, , , ,1, , , ,1, , , ,1,
//  ,1, , , ,1,2, , , , ,1,1, , , , , , ,1,
//  ,1, , , ,1, , , , , ,3,1, , , , , , ,1,
//  ,1, ,1,1,2, , , , , , ,1, , , , , , ,1,
// 1,2, , , , , , ,1, , , ,1,1,1,1, , , ,1, 
// 1, , , ,1,1, , , , , , , , , ,1, , , ,1,
// 1, , ,1,2, , , , , , , , , , ,1, , , ,1,
// 1, , ,1, , , , , , , , , , , ,1, , , ,1,
// 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1};
// One entry in the array represents 1 unit squared of 3D World Space
// so when a 1 is encountered with zeros all around it 4 polygons are
// created for the four walls of a cube all facing outwards.
//
// If a number other than zero is to any side of the 1 then a wall is
// not built for that side because it is covered up by an adjacent wall.
// So in other words each 1 digit represent a 1x1 cube in world space
// and we will texture the four walls (n,s,e & w) with some brick wall
// texture.
//
// The 2 and 3's in the map were just put in there by me at the last
// minute to give the map a few angles. A 2 digit represents a NE
// facing wall and a 3 represents a NW facing wall. I didn't bother to
// create SW or SE but you can do that yourself if you want. Just build
// them the same as the NW and NE walls but reverse the winding order
// of the vertices.
//
// The polygons are created in WORLD space with the center of space 0,0,0
// being in the middle of the map and each digit as I said represents
// 1x1 unit in space.The full grid is 20x40 in dimensions (not all
// shown here).


// Loop through the
void InitPolygons(void)
{
    D3DLVERTEX VERTLIST[4][4];
    PolygonList=NULL;// this is a GLOBAL pointer
    POLYGON *child=NULL;
    int direction[4];
    // Loop over map
    for (int y=0;y< 40;y++)
    {
        for (int x=0;x< 20;x++)
        {
            ZeroMemory(direction,sizeof(int)*4);
            int offset=(y*20)+x;
            // check what the digit is in the current map location
            if (BSPMAP[offset]!=0)
            {
                if (BSPMAP[offset]==2)// North East Wall
                {
                    // well all this time i thought he was doing a DOOM engine but he was doing a QUAKE engine in 3D... because these polygons are 3D..
                    // Each "wall" is four vertices
                    VERTLIST[0][0]=D3DLVERTEX(D3DVECTOR(x -10.5f, 3.0f, (20.0f - y) - 0.5f), RGB_MAKE( 255, 255, 255), 0, 0, 0);
                    VERTLIST[0][1]=D3DLVERTEX(D3DVECTOR(x -9.5f,  3.0f, (20.0f - y) + 0.5f), RGB_MAKE( 255, 255, 255), 0, 1, 0);
                    VERTLIST[0][2]=D3DLVERTEX(D3DVECTOR(x -9.5f,  0.0f, (20.0f - y) + 0.5f), RGB_MAKE( 255, 255, 255), 0, 1, 1);
                    VERTLIST[0][3]=D3DLVERTEX(D3DVECTOR(x -10.5f, 0.0f, (20.0f - y) - 0.5f), RGB_MAKE( 255, 255, 255), 0, 0, 1);
                    direction[0]=1;
                }
                if (BSPMAP[offset]==3)// North West Wall
                {	
                    VERTLIST[0][0]=D3DLVERTEX(D3DVECTOR(x-10.5f,3.0f,(20.0f-y)+0.5f),RGB_MAKE( 255, 255, 255),0,0,0);
                    VERTLIST[0][1]=D3DLVERTEX(D3DVECTOR(x-9.5f,3.0f,(20.0f-y)-0.5f),RGB_MAKE( 255, 255, 255),0,1,0);
                    VERTLIST[0][2]=D3DLVERTEX(D3DVECTOR(x-9.5f,0.0f,(20.0f-y)-0.5f),RGB_MAKE( 255, 255, 255),0,1,1);
                    VERTLIST[0][3]=D3DLVERTEX(D3DVECTOR(x-10.5f,0.0f,(20.0f-y)+0.5f),RGB_MAKE( 255, 255, 255),0,0,1);
                    direction[0]=1;
                }	

                if (BSPMAP[offset]==1)// Its a Standared wall
                {
                    if (x > 0)
                    {
                        if (BSPMAP[offset-1]==0)// if theres nothing to the left add a left facing wall
                        {
                            VERTLIST[0][0]=D3DLVERTEX(D3DVECTOR(x-10.5f,3.0f,(20.0f-y)+0.5f),RGB_MAKE(255,255,255),0,0,0);
                            VERTLIST[0][1]=D3DLVERTEX(D3DVECTOR(x-10.5f,3.0f,(20.0f-y)-0.5f),RGB_MAKE(255,255,255),0,1,0);
                            VERTLIST[0][2]=D3DLVERTEX(D3DVECTOR(x-10.5f,0.0f,(20.0f-y)-0.5f),RGB_MAKE(255,255,255),0,1,1);
                            VERTLIST[0][3]=D3DLVERTEX(D3DVECTOR(x-10.5f,0.0f,(20.0f-y)+0.5f),RGB_MAKE(255,255,255),0,0,1);
                            direction[0]=1;
                        }
                    }
                    if (x < 19)
                    {
                        if (BSPMAP[offset+1]==0)// if there is nothing to the right add a right facing wall
                        {
                            VERTLIST[1][0]=D3DLVERTEX(D3DVECTOR(x-9.5f,3.0f,(20.0f-y)-0.5f),RGB_MAKE(255,255,255),0,0,0);
                            VERTLIST[1][1]=D3DLVERTEX(D3DVECTOR(x-9.5f,3.0f,(20.0f-y)+0.5f),RGB_MAKE(255,255,255),0,1,0);
                            VERTLIST[1][2]=D3DLVERTEX(D3DVECTOR(x-9.5f,0.0f,(20.0f-y)+0.5f),RGB_MAKE(255,255,255),0,1,1);
                            VERTLIST[1][3]=D3DLVERTEX(D3DVECTOR(x-9.5f,0.0f,(20.0f-y)-0.5f),RGB_MAKE(255,255,255),0,0,1);
                            direction[1]=1;
                        }
                    }
                    if (y > 0)
                    {
                        if (BSPMAP[offset-20]==0)// if there is nothing south add a south facing wall
                        {
                            VERTLIST[2][0]=D3DLVERTEX(D3DVECTOR(x-9.5f,3.0f,(20.0f-y)+0.5f),RGB_MAKE(255,255,255),0,0,0);
                            VERTLIST[2][1]=D3DLVERTEX(D3DVECTOR(x-10.5f,3.0f,(20.0f-y)+0.5f),RGB_MAKE(255,255,255),0,1,0);
                            VERTLIST[2][2]=D3DLVERTEX(D3DVECTOR(x-10.5f,0.0f,(20.0f-y)+0.5f),RGB_MAKE(255,255,255),0,1,1);
                            VERTLIST[2][3]=D3DLVERTEX(D3DVECTOR(x-9.5f,0.0f,(20.0f-y)+0.5f),RGB_MAKE( 255, 255, 255),0,0,1);
                            direction[2]=1;;
                        }
                    }
                    if(y < 39)
                    {	
                        if (BSPMAP[offset+20]==0)// if there is nothing to the north add a north facing wall
                        {
                            VERTLIST[3][0]=D3DLVERTEX(D3DVECTOR(x-10.5f,3.0f,(20.0f-y)-0.5f),RGB_MAKE(255,255,255),0,0,0);
                            VERTLIST[3][1]=D3DLVERTEX(D3DVECTOR(x-9.5f,3.0f,(20.0f-y)-0.5f),RGB_MAKE(255, 255, 255),0,1,0);
                            VERTLIST[3][2]=D3DLVERTEX(D3DVECTOR(x-9.5f,0.0f,(20.0f-y)-0.5f),RGB_MAKE( 255, 255, 255),0,1,1);
                            VERTLIST[3][3]=D3DLVERTEX(D3DVECTOR(x-10.5f,0.0f,(20.0f-y)-0.5f),RGB_MAKE( 255, 255, 255),0,0,1);
                            direction[3]=1;;
                        }
                    }	
                }// end for if offset==1

                // build the polygons

                for (int a=0;a<4;a++)
                {
                    if (direction[a]!=0)
                    {
                        if (PolygonList==NULL)
                        {
                            PolygonList=AddPolygon(NULL,&VERTLIST[a][0],4);
                            child=PolygonList;
                        }
                        else
                        {
                            child=AddPolygon(child,&VERTLIST[a][0],4);
                        }
                    }//
                }////
            }// end for if offset!=0
        }
    }

    // Compile the BSP Tree from the linked list of polygons
    BSPTreeRootNode=new NODE;
    BuildBspTree(BSPTreeRootNode,PolygonList);
}

// This is the meat, it can take a polygon and convert it into triangles
POLYGON * AddPolygon(POLYGON* Parent, D3DLVERTEX *Vertices, WORD NOV)
{
    int loop;
    POLYGON * Child=new POLYGON;
    Child-> NumberOfVertices=NOV;
    // eg 4 walls, 4 vertices, (4-2) * 3 = 6, 6 points in the 2 triangles needed
    Child-> NumberOfIndices=(NOV-2)*3;
    Child-> Next=NULL;

    // Add the vertex list
    for (loop=0;loop< NOV;loop++)
    {
        Child-> VertexList[loop]=Vertices[loop];
    } 

    // TODO: Break this into its own function! Nice to have!
    // calculate indices of triangles
    // each value in Indices is actually an index in Vertices
    WORD v0,v1,v2;
    for (loop=0;loop< Child-> NumberOfIndices/3;loop++)
    {
        if (loop==0)
        {
            v0=0;
            v1=1;
            v2=2;
        }
        else
        {
            v1=v2;
            v2++;
        }
        Child-> Indices[loop*3]=v0;
        Child-> Indices[(loop*3)+1]=v1;
        Child-> Indices[(loop*3)+2]=v2;
    }

    // CROSS PRODUCT to
    // generate polygon normal
    // TODO: I don't understand this
    // OK: so i guess its actually taking the 2D plane and getting the 3D Normal
    // So if its is a square on a 2D plane built in X and Y coords, the Cross is a Z vector
    // https://www.opengl.org/discussion_boards/showthread.php/159259-How-to-Calculate-Polygon-Normal
    // Hello there
    // Well its quite simple. Take any three vertices make sure that you are following a consistent winding
    // order; either clockwise or anti clockwise. Create two new vectors by subtracting the second vertex
    // from the first and then the third from the first. Then do a simple cross product between the two new vectors.
    // Here is the pseudocode.
    // Code :
    // Vector GetNormal(Vector v1, Vector v2, Vector v3)
    // {
    //     Vector a,b;
    //     a = v1 - v2;
    //     b = v1 - v3;
    //     return Cross(a,b);   
    // }
    // This is used later for DOT PRODUCTS
    D3DVECTOR * vec0=(D3DVECTOR *) &Child->VertexList[0];
    D3DVECTOR * vec1=(D3DVECTOR *) &Child->VertexList[1];
    D3DVECTOR * vec2=(D3DVECTOR *) &Child->VertexList[Child->NumberOfVertices-1];// the last vert
    D3DVECTOR edge1=(*vec1)-(*vec0);
    D3DVECTOR edge2=(*vec2)-(*vec0);
    Child->Normal=CrossProduct(edge1,edge2);
    Child->Normal=Normalize(Child->Normal);

    // Continue linked list
    if (Parent!=NULL)
    {
        Parent->Next=Child;
    }

    return Child;
}



// Helper function to test which side of a polygon the pos is on
//
// A point is said to lay behind a plane if it is on the opposite
// side of the plane to the side the plane Normal is facing.
// if a plane faces left (because the Normal faces left) a point on
// the right side of the plane will be Behind the plane.
// If it is on the right side of this plane then the point is said
// to lay In Front of the plane.
// If the point lay exactly on the plane then it is said to be
// 'Coincident' with the plane and is neither in front or behind
int ClassifyPoint(D3DVECTOR *pos,POLYGON * Plane)
{
    float result;
    // pick an point on the plane, a vertex point suffices
    D3DVECTOR *vec1=(D3DVECTOR *)&Plane-> VertexList[0];
    // calculate the direction from the pos to the vertex point
    D3DVECTOR Direction=(*vec1)-(*pos);
    // dot product calculates length of project of direction onto plane normal
    // ie, if the length is negative its in front, positive its behind, and 0 its coincident
    // scalar result
    result=DotProduct(Direction,Plane->Normal);
    // fuzzy comparison for float point errors
    if (result< -0.001)
        return CP_FRONT;
    if (result> 0.001)
        return CP_BACK;
    return CP_ONPLANE;
}

// Helper function to determine if a polygon overlaps another polygon (needs to be split)
//
// if all points behind, we would put whole poly in back list
// if all points ahead, we would put whole poly in front list
// if overlap, split and put into both
//
int ClassifyPoly(POLYGON *Plane,POLYGON * Poly)
{
    int Infront=0;
    int Behind=0;
    int OnPlane=0;
    float result;
    D3DVECTOR *vec1=(D3DVECTOR *)&Plane->VertexList[0];
    for (int a=0;aNumberOfVertices;a++)
    {
        D3DVECTOR *vec2=(D3DVECTOR *)&Poly->VertexList[a];
        D3DVECTOR Direction=(*vec1)-(*vec2);
        result=DotProduct(Direction,Plane->Normal);
        if (result> 0.001)
        {
            Behind++;
        }
        else if (result< -0.001)
        {
            Infront++;
        }
        else
        {
            OnPlane++;
            Infront++;
            Behind++;
        }
    }
    if (OnPlane==Poly-> NumberOfVertices)
        // return front because if its on the same plane we will put it down the front list
        return CP_FRONT;// this would nomrally be CP_ONPLANE
    if (Behind==Poly-> NumberOfVertices)
        return CP_BACK;
    if (Infront==Poly-> NumberOfVertices)
        return CP_FRONT;
    return CP_SPANNING;
}

// Helper Will lead to 
void SplitPolygon(POLYGON *Poly,POLYGON *Plane,POLYGON *FrontSplit,POLYGON *BackSplit);
// TBD

// Helper function to pick best "splitter" polygon out of a list of polygons
// seems trivial but very important when dealing with 1000s of polygons
// Splitters have the power to split polygons into new polygons, so we will
// be creating polygons. So we need to choose a splitter that will subdivide as
// little as feasible, otherwise as the tree deepens are polygon count expands and expands
// Determining the perfect splitter is impossible as it is not scalable
// Instead for each immediate list in a Node we will check to see how many splits it would
// make, we then choose a poly that would produce the least splits in that immediate node's list
// Not perfect, but doable
// IN ADDITION, balancing the tree is important so as to reduce the depth of the tree
// 32 polys unbalanced can lead to a single depth of 32 nods
// 32 polys balanced will lead to depth of 4 or 5 maybe
// HOWEVER, a balanced splitter may produce more polys -- SHEESH
//
// score=abs(frontfaces-backfaces)+(splits*8)
// abs(frontfaces-backfaces), the higher this value the more unbalanced
// splits are multiplied by 8 to give them more importance than balancing
//
POLYGON * SelectBestSplitter(POLYGON *PolyList)
{
    // start our candidate splitter at the front of the linked list
    POLYGON* Splitter=PolyList;
    POLYGON* CurrentPoly=NULL;
    unsigned long BestScore=100000;// just set to a very high value to begin
    POLYGON * SelectedPoly=NULL; 
    while (Splitter!=NULL)
    {
        // start comparing our splitter to the poly list
        CurrentPoly=PolyList;
        unsigned long score,splits,backfaces,frontfaces;
        score=splits=backfaces=frontfaces=0;
        while (CurrentPoly!=NULL)
        {
            // skip self comparison
            if (CurrentPoly!=Splitter)
            {
                // see if poly is in front or behind or spanning
                int result=ClassifyPoly(Splitter,CurrentPoly);
                // increment the number of fronts, backs and splits this splitter would produce
                switch ( result)
                {
                    // on plane does not return for ClassifyPoly, we default to front
                    case CP_ONPLANE:
                        break;
                    case CP_FRONT:
                        frontfaces++;
                        break;
                    case CP_BACK:
                        backfaces++;
                        break;
                    case CP_SPANNING:
                        splits++;
                        break;
                    default:
                        break;
                }
            }
            CurrentPoly=CurrentPoly-> Next;
        }// end while current poly
        // calculate our score for this candidate splitter
        score=abs(frontfaces-backfaces)+(splits*8);
        if (score< BestScore)
        {
            // if its better than a predecessor set this candidate as the current, best splitter
            BestScore=score;
            SelectedPoly=Splitter;
        }
        Splitter=Splitter-> Next;
    }// end while splitter == null	

    // a candidate has settled as the best, return it
    return SelectedPoly;
}


// used when splitting a poly
// takes a line, a vertex to test from and the normal of the vertex
// creates an intersection point (if they intersect) and how far along the line it occurred
bool Get_Intersect (D3DVECTOR *linestart,D3DVECTOR *lineend,D3DVECTOR *vertex,D3DVECTOR *normal,D3DVECTOR * intersection, float *percentage)
{
    D3DVECTOR direction,L1;
    float linelength,dist_from_plane;

    direction.x=lineend->x-linestart->x;
    direction.y=lineend->y-linestart->y;
    direction.z=lineend->z-linestart->z;

    linelength=DotProduct(direction,*normal);

    if (fabsf(linelength)<0.0001)
    {
        return false;
    }

    L1.x=vertex->x-linestart->x;
    L1.y=vertex->y-linestart->y;
    L1.z=vertex->z-linestart->z;

    dist_from_plane=DotProduct(L1,*normal);
    *percentage=dist_from_plane/linelength; 

    if (*percentage<0.0f) 
    {
        return false;
    }
    else if (*percentage>1.0f) 
    {
        return false;
    }

    intersection->x=linestart->x+direction.x*(*percentage);
    intersection->y=linestart->y+direction.y*(*percentage);
    intersection->z=linestart->z+direction.z*(*percentage);
    return true;
}


// poly needs to be split, plane is the splitter poly, 
void SplitPolygon(POLYGON *Poly,POLYGON *Plane,POLYGON *FrontSplit,POLYGON *BackSplit)
{
    // front list will be all vertices that will belong to the front poly split, etc for back
    D3DLVERTEX FrontList[20],BackList[20],FirstVertex;
    D3DVECTOR PlaneNormal,IntersectPoint,PointOnPlane,PointA,PointB;
    WORD FrontCounter=0,BackCounter=0,loop=0,CurrentVertex=0;
    float percent;	

    // Find any vertex on the plane to use later in plane intersect routine
    PointOnPlane=*(D3DVECTOR *)&Plane->VertexList[0]; // cast vertex to vector so we can use GetIntersect

    // first we find out if the first vertex belongs in front or back list
    FirstVertex=Poly->VertexList[0];
    switch (ClassifyPoint( (D3DVECTOR *)&FirstVertex,Plane))
    {
        case CP_FRONT:
            FrontList[FrontCounter++]=FirstVertex; // post increment
            break;
        case CP_BACK:
            BackList[BackCounter++]=FirstVertex;
            break;
        case CP_ONPLANE:
            BackList[BackCounter++]=FirstVertex;
            FrontList[FrontCounter++]=FirstVertex;
            break;
        default:
            break;
    }

    // loop through remaining vertices
    for (loop=1;loop<Poly->NumberOfVertices+1;loop++)
    {
        // on the last iteration pair the last vertices with the first
        if (loop==Poly->NumberOfVertices) 
        {
            CurrentVertex=0;
        }
        else
        {
            CurrentVertex=loop;
        }
        // get our 2 points for comparison
        PointA=*(D3DVECTOR *)&Poly->VertexList[loop-1];
        PointB=*(D3DVECTOR *)&Poly->VertexList[CurrentVertex];

        // test our second point in the pair
        int Result=ClassifyPoint(&PointB,Plane);
        if (Result==CP_ONPLANE)
        {
            // if its on the same plane then add it to both lists since it will be a part of both created polygons
            BackList[BackCounter++]=Poly->VertexList[CurrentVertex];
            FrontList[FrontCounter++]=Poly->VertexList[CurrentVertex];
        }
        else
        {
            // if not on plane lets test our line between both points and see if we get an intersection
            if (Get_Intersect(&PointA,&PointB,&PointOnPlane,&PlaneNormal,&IntersectPoint, &percent)==true)
            {
                // WTF guide on textures and what?
                // I think we can ignore the texture setting for the vertex and pay attention to the coord elements
                float deltax,deltay,texx,texy;
                deltax = Poly->VertexList[CurrentVertex].tu - Poly->VertexList[loop-1].tu;
                deltay = Poly->VertexList[CurrentVertex].tv - Poly->VertexList[loop-1].tv;
                texx = Poly->VertexList[loop-1].tu+(deltax*percent);
                texy = Poly->VertexList[loop-1].tv+(deltay*percent);
                // Copy is a vertex at the intersection point
                D3DLVERTEX copy = D3DLVERTEX(IntersectPoint,RGB_MAKE(255,255,255),0,texx,texy);

                if (Result==CP_FRONT )
                {
                    // put the intersection point into both new poly lists
                    BackList[BackCounter++]=copy;
                    FrontList[FrontCounter++]=copy;
                    if (CurrentVertex!=0)
                    {
                        // then stick our originally checked point in the front
                        FrontList[FrontCounter++]=Poly->VertexList[CurrentVertex];
                    }
                }

                if (Result==CP_BACK)
                {
                    // put the intersection point into both new poly lists
                    FrontList[FrontCounter++]=copy;
                    BackList[BackCounter++]=copy;	
                    if (CurrentVertex!=0)
                    {
                        // then stick our originally checked point in the back
                        BackList[BackCounter++]=Poly->VertexList[CurrentVertex];
                    }
                }	

            }// end if intersection (get intersect==true)
            else
            {
                // if no intersection (and not on same plane), just simply stick the vertex in the appropriate list
                // dont stick the first vertex in a list since it was already done
                if (Result==CP_FRONT)
                {
                    if (CurrentVertex!=0)
                    {
                        FrontList[FrontCounter++]=Poly->VertexList[CurrentVertex];
                    }
                }

                if (Result==CP_BACK) 
                {
                    if (CurrentVertex!=0)
                    {
                        BackList[BackCounter++]=Poly->VertexList[CurrentVertex];
                    }
                }
            }

        } // not on plane
    }//end loop through each edge

    // At this point all vertices have been placed in the front and back lists
    // Now we build 2 new polygons for this list

    //OK THEN LETS BUILD THESE TWO POLYGONAL BAD BOYS

    FrontSplit->NumberOfVertices=0;
    BackSplit->NumberOfVertices=0;

    for (loop=0;loop<FrontCounter;loop++)
    {
        FrontSplit->NumberOfVertices++;
        FrontSplit->VertexList[loop]=FrontList[loop];
    }

    for (loop=0;loop<BackCounter;loop++)
    {
        BackSplit->NumberOfVertices++;
        BackSplit->VertexList[loop]=BackList[loop];
    }

    BackSplit->NumberOfIndices=(BackSplit->NumberOfVertices-2)*3;
    FrontSplit->NumberOfIndices=(FrontSplit->NumberOfVertices-2)*3;

    // Fill in the Indices Array

    WORD v0,v1,v2;
    for (loop=0;loop<FrontSplit->NumberOfIndices/3;loop++)
    {
        if (loop==0)
        {
            v0=0;
            v1=1;
            v2=2;
        }
        else
        {
            v1=v2;
            v2++;
        }
        FrontSplit->Indices[loop*3]=v0;
        FrontSplit->Indices[(loop*3)+1]=v1;
        FrontSplit->Indices[(loop*3)+2]=v2;
    }

    for (loop=0;loop<BackSplit->NumberOfIndices/3;loop++)
    {
        if (loop==0) 
        {
            v0=0;
            v1=1;
            v2=2;
        }
        else
        {
            v1=v2;
            v2++;
        }
        BackSplit->Indices[loop*3]=v0;
        BackSplit->Indices[(loop*3)+1]=v1;
        BackSplit->Indices[(loop*3)+2]=v2;
    }

    // calculate polygon Normals

    D3DVECTOR edge1,edge2;
    edge1=*(D3DVECTOR *)&FrontSplit->VertexList[FrontSplit->Indices[1]]-*(D3DVECTOR *)&FrontSplit->VertexList[FrontSplit->Indices[0]];

    edge2=*(D3DVECTOR *)&FrontSplit->VertexList[FrontSplit->Indices[FrontSplit->NumberOfIndices-1]]-*(D3DVECTOR *)&FrontSplit->VertexList[FrontSplit->Indices[0]];

    FrontSplit->Normal=CrossProduct(edge1,edge2);
    FrontSplit->Normal=Normalize(FrontSplit->Normal);

    edge1=*(D3DVECTOR *)&BackSplit->VertexList[BackSplit->Indices[1]]-*(D3DVECTOR *)&BackSplit->VertexList[BackSplit->Indices[0]];

    edge2=*(D3DVECTOR *)&BackSplit->VertexList[BackSplit->Indices[BackSplit->NumberOfIndices-1]]-*(D3DVECTOR *)&BackSplit->VertexList[BackSplit->Indices[0]];

    BackSplit->Normal=CrossProduct(edge1,edge2);
    BackSplit->Normal=Normalize(BackSplit->Normal);
}






void BuildBspTree(NODE * CurrentNode, POLYGON * PolyList)
{
    POLYGON *polyTest=NULL;
    POLYGON *FrontList=NULL;
    POLYGON *BackList=NULL;
    POLYGON *NextPolygon=NULL;
    POLYGON *FrontSplit=NULL;
    POLYGON *BackSplit=NULL;
    D3DVECTOR vec1,vec2;
    // assign a splitter poly from the list of polys
    CurrentNode-> Splitter = SelectBestSplitter(PolyList);
    polyTest=PolyList;

    while (polyTest!=NULL)
    {
        NextPolygon = polyTest-> Next;// remember because polytest-> Next will be altered

        // skip the splitter
        if (polyTest!=CurrentNode-> Splitter)
        {
            // Get which list it will fall into
            switch (ClassifyPoly(CurrentNode-> Splitter,polyTest))
            {
                // This node belongs in the front so put it in the front list
                // do this with some weird reasoning for putting it at the beginning of the linked list
                case CP_FRONT:
                    // stick polytest at the beginning of the front list
                    polyTest-> Next=FrontList;
                    FrontList=polyTest;	
                    break;
                case CP_BACK:
                    // stick polytest at the beginning of the back list
                    polyTest-> Next=BackList;
                    BackList=polyTest;	
                    break;
                case CP_SPANNING:
                    // create two new polygons from the split line
                    FrontSplit=new POLYGON;
                    BackSplit=new POLYGON;
                    ZeroMemory(FrontSplit,sizeof(POLYGON));
                    ZeroMemory(BackSplit,sizeof(POLYGON));
                    SplitPolygon(polyTest,CurrentNode-> Splitter,FrontSplit,BackSplit);
                    delete polyTest;
                    // put the front poly in the beginning of the front list
                    FrontSplit-> Next=FrontList;
                    FrontList=FrontSplit;
                    // put the back poly in the beginning of the back list
                    BackSplit-> Next=BackList;
                    BackList=BackSplit;
                    break;
                default:
                    break;
            }
        }// end if polypoint!=CurrentNodesplitter

        // look at the next polygon from the original list
        polyTest = NextPolygon;
    }// end while loop

    // At this point the polygons have been split and separated and all placed in front or back lists

    if (FrontList==NULL)
    {
        // If we have nothing in the front then we create a final leaf node and set it to empty space
        NODE *leafnode=new NODE;
        ZeroMemory(leafnode,sizeof(leafnode));
        leafnode-> IsLeaf=true;
        leafnode-> IsSolid=false;	
        CurrentNode-> Front=leafnode;
    }
    else
    {
        // If we do have front polygons create a new node and recurse the front list into the new node
        NODE * newnode=new NODE;
        ZeroMemory(newnode,sizeof(newnode));
        newnode-> IsLeaf=false;
        CurrentNode-> Front=newnode;
        BuildBspTree(newnode,FrontList);
    }

    if (BackList==NULL)
    {
        // If we have nothing else behind us designate a leaf node behind us and set it to solid space
        NODE *leafnode=new NODE;
        ZeroMemory(leafnode,sizeof(leafnode));
        leafnode-> IsLeaf=true;
        leafnode-> IsSolid=true;	
        CurrentNode-> Back=leafnode;;
    }
    else
    {
        // If we have polys behind recurse them into a new tree behind us
        NODE * newnode=new NODE;
        ZeroMemory(newnode,sizeof(newnode));
        newnode-> IsLeaf=false;
        CurrentNode-> Back=newnode;
        BuildBspTree(newnode,BackList);
    }
}// end function




// Example Back to Front rendering

void WalkBspTree(NODE *Node,D3DVECTOR *pos) // pos = camera position
{
    // if a leaf, then no polygons to render
    if (Node->IsLeaf==true)
        return;

    // get side camera is on
    int result=ClassifyPoint(pos,Node->Splitter);

    // if on the front we will render everything on the back side of the node
    // Switching this to CP_BACK will reverse this and make a Front to Back renderer (like doom), but issues with transparency merging
    if (result==CP_FRONT)
    {
        //we recurse first so we draw further away first
        if (Node->Back!=NULL)
            WalkBspTree(Node->Back,pos);

        // draw ourselves
        // If switching to CP_BACK for front to back rendering above, then this would go down to below the other recursions
        lpDevice->DrawIndexedPrimitive(D3DPT_TRIANGLELIST,D3DFVF_LVERTEX,&Node->Splitter->VertexList[0],Node->Splitter->NumberOfVertices,&Node->Splitter->Indices[0],Node->Splitter->NumberOfIndices,NULL);

        // then draw in the front
        if (Node->Front!=NULL)
            WalkBspTree(Node->Front,pos);
        return ;
    } // this happens if we are at back or on plane

    // if we are behind it then draw from front to back
    if (Node->Front!=NULL)
        WalkBspTree(Node->Front,pos);
    // OPTION: put rendering here for front to back rendering
    if (Node->Back!=NULL)
        WalkBspTree(Node->Back,pos);

    return;

    // NOTE, switching from front to back rendering would cause further walls to be drawn on top of closer walls
    // code above is a back to front renderer to deal with this
    // Doom was a front to back renderer but had a listing of all vertical pixels (x coords) drawn to the screen
    // it would then only draw a wall if it had a projected screen coordinate (x) that as not already drawn to the screen
    // I think it was a linked list of pairs of values that were drawn (may get more expensive the higher the resolution)
    // (though rendering at 640x480 and just upscaling to the monitor res is not a bad thing)
    // (0 - 122) -> (145 - 245) -> (430 - 480)
}


// CHEAP COLLISION DETECTION, Line of Sight

// Takes two points to compare and the BSP tree node at the start
bool LineOfSight (D3DVECTOR *Start,D3DVECTOR *End, NODE *Node)
{
    float temp;
    D3DVECTOR intersection;
    // if we have traversed the tree to a node and its empty return true LoS
    if (Node->IsLeaf==true)
    {
        return !Node->IsSolid;
    }

    // Figure out which sides of the polygon splitter line our two points fall to 
    int PointA=ClassifyPoint(Start,Node->Splitter);
    int PointB=ClassifyPoint(End,Node->Splitter);

    // If they are both on the same plane as the splitter then recurse LineOfSight on the front node (same as both on front below)
    if (PointA==CP_ONPLANE && PointB==CP_ONPLANE)
    {
        return LineOfSight(Start,End,Node->Front);
    }

    // if separated we need to get the intersection of where
    if (PointA==CP_FRONT && PointB==CP_BACK)
    {
        Get_Intersect (Start,End,(D3DVECTOR *) &Node->Splitter->VertexList[0],&Node->Splitter->Normal,&intersection,&temp);
        // then we check the line of sight and its only true if both the start and intersection and end and intersection can be seen (no solid areas in between)
        // NOTE it appears that just having a splitter between us is not enough to detect if there was LoS block, we have to confirm solid space
        return LineOfSight(Start,&intersection,Node->Front) && LineOfSight(End,&intersection,Node->Back) ;
    }

    // same if separated here just with end before start pos
    if (PointA==CP_BACK && PointB==CP_FRONT)
    {
        Get_Intersect (Start,End,(D3DVECTOR *) &Node->Splitter->VertexList[0],&Node->Splitter->Normal,&intersection,&temp);
        return LineOfSight(End,&intersection,Node->Front) && LineOfSight(Start,&intersection,Node->Back) ;
    }

    // if we get here one of the points is on the plane
    if (PointA==CP_FRONT || PointB==CP_FRONT)
    {
        return LineOfSight(Start,End,Node->Front);
    }
    else
    {
        return LineOfSight(Start,End,Node->Back);
    }

    return true;
}

// NOTE, how do I use this for collision dection with a single pos?
// We can test a potential position by seeing if it ultimately passes to a leaf that is empty or solid for movement
// LoS above is useful for seeing if a line of sight or raycast collides with a solid mass
// NOTE: can we figure out which plane (wall) it struck?


// NOTE: Axis Aligned Bounding Boxes to peform very quick Fustrum Rejection of entire sections of the tree speeding up rendering by a very large amount.

