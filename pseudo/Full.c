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
                    VERTLIST[0][0]=D3DLVERTEX(D3DVECTOR(x-10.5f,3.0f,(20.0f-y)-0.5f),RGB_MAKE( 255, 255, 255),0,0,0);
                    VERTLIST[0][1]=D3DLVERTEX(D3DVECTOR(x-9.5f,3.0f,(20.0f-y)+0.5f),RGB_MAKE( 255, 255, 255),0,1,0);
                    VERTLIST[0][2]=D3DLVERTEX(D3DVECTOR(x-9.5f,0.0f,(20.0f-y)+0.5f),RGB_MAKE( 255, 255, 255),0,1,1);
                    VERTLIST[0][3]=D3DLVERTEX(D3DVECTOR(x-10.5f,0.0f,(20.0f-y)-0.5f),RGB_MAKE( 255, 255, 255),0,0,1);
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
    // Well its quite simple. Take any three vertices make sure that you are following a consistent winding order; either clockwise or anti clockwise. Create two new vectors by subtracting the second vertex from the first and then the third from the first. Then do a simple cross product between the two new vectors.
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



