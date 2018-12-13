void WalkBspTree(NODE *Node,D3DVECTOR *pos)
{
    POLYGON *shared;
    // figure out which sode of the splitter we are on
    int result=ClassifyPoint(pos,Node-> Splitter);

    if (result==CP_FRONT)
    {
        // render back node tree first we are in front
        shared=Node-> Splitter->SameFacingShared;
        if (Node-> Back!=NULL)
            WalkBspTree(Node-> Back,pos);
        
        // render us
        lpDevice-> DrawIndexedPrimitive(D3DPT_TRIANGLELIST,D3DFVF_LVERTEX,&Node-> Splitter-> VertexList[0],Node-> Splitter-> NumberOfVertices,&Node-> Splitter->Indices[0],Node-> Splitter-> NumberOfIndices,NULL);

        // render same planes facing same way
        while (shared!=NULL)
        {
            lpDevice-> DrawIndexedPrimitive(D3DPT_TRIANGLELIST,D3DFVF_LVERTEX,&shared-> VertexList[0],shared-> NumberOfVertices,&shared-> Indices[0],shared-> NumberOfIndices,NULL);
            shared=shared-> SameFacingShared;
        }

        // render front
        if (Node->Front!=NULL)
            WalkBspTree(Node->Front,pos);

        return ;
    }

    // this means we are at back of node 
    // render front first
    shared=Node->Splitter->OppositeFacingShared;
    if (Node->Front!=NULL)
        WalkBspTree(Node->Front,pos);

    // render same planes facing same way
    while (shared!=NULL)
    {
        lpDevice-> DrawIndexedPrimitive(D3DPT_TRIANGLELIST,D3DFVF_LVERTEX,&shared-> VertexList[0],shared-> NumberOfVertices,&shared-> Indices[0],shared-> NumberOfIndices,NULL);
        shared=shared-> OppositeFacingShared;
    } 

    // DONT render us since its culled

    // render back second
    if (Node-> Back!=NULL)
        WalkBspTree(Node->Back,pos);
        return;
}