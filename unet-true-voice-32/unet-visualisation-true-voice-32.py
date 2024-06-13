
import sys
sys.path.append('../')
from pycore.tikzeng import *
from pycore.blocks  import *

arch = [ 
    to_head('..'), 
    to_cor(),
    to_begin(),
    
    #input
    to_input( '../examples/fcn8s/cats.jpg' ),




    #block-000: double conv only 1->32
    to_ConvConvRelu( 
        name='ccr_b1', ###############
        s_filer=256, 
        n_filer=(32,32), 
        offset="(0,0,0)", to="(0,0,0)", 
        width=(2,2), height=40, depth=40  ),

    # #arrow
    # to_connection( "temp", "ccr_b1"),

    #block-001: maxpool + double conv 32->64
    to_Pool(
        name="pool_b1", ##############
        offset="(1,0,0)", 
        to="(ccr_b1-east)", #################
        width=1, height=32, depth=32, opacity=0.5),
    
    #arrow
    to_connection( "ccr_b1", "pool_b1"),

    # *block_2ConvPool( 
    #     name='b2', ##############
    #     botton='pool_b1', ##############
    #     top='pool_b2', ##############
    #     s_filer=128, 
    #     n_filer=64, 
    #     offset="(1,0,0)", size=(32,32,3.5), opacity=0.5 ),

    # [
    to_ConvConvRelu( 
        name="ccr_b2",
        s_filer=str(128), 
        n_filer=(64,64), 
        offset="(0,0,0)", 
        to="(pool_b1-east)", 
        width=(3.5, 3.5), 
        height=32, 
        depth=32,   
        ),    

    #block-002: maxpool + double conv 64->128
    to_Pool(         
        name="pool_b2", 
        offset="(1,0,0)", 
        to="(ccr_b2-east)",  
        width=1,         
        height=32 - 8, 
        depth=32 - 8, 
        opacity=0.5, 
        ),

    # arrow
    to_connection( 
        # "pool_b1", 
        "ccr_b2",
        "pool_b2"
        ),
    # ],

    # *block_2ConvPool( 
    #     name='b3', ##############
    #     botton='pool_b2', ############## 
    #     top='pool_b3', ##############
    #     s_filer=64, 
    #     n_filer=128, 
    #     offset="(0,0,0)", 
    #     size=(32 - 8, 32 - 8, 4.5), 
    #     opacity=0.5 ),

    # [
    to_ConvConvRelu( 
        name="ccr_b3",
        s_filer=str(64), 
        n_filer=(128,128), 
        offset="(0,0,0)", 
        to="(pool_b2-east)", 
        width=(3.5, 3.5), 
        height=32 - 8, 
        depth=32 - 8,   
        ),    

    #block-003: maxpool + double conv 128->256
    to_Pool(         
        name="pool_b3", 
        offset="(1,0,0)", 
        to="(ccr_b3-east)",  
        width=1,         
        height=32 - 16, 
        depth=32 - 16, 
        opacity=0.5, 
        ),

    # arrow
    to_connection( 
        # "pool_b2",
        "ccr_b3",
        "pool_b3"
        ),
    # ],

    # *block_2ConvPool( 
    #     name='b4', ##############
    #     botton='pool_b3', ##############
    #     top='pool_b4', ##############
    #     s_filer=32,  
    #     n_filer=256, 
    #     offset="(1,0,0)", size=(16,16,5.5), opacity=0.5 ),

    # [
    to_ConvConvRelu( 
        name="ccr_b4",
        s_filer=str(32), 
        n_filer=(256,256), 
        offset="(0,0,0)", 
        to="(pool_b3-east)", 
        width=(3.5, 3.5), 
        height=32 - 16, 
        depth=32 - 16,   
        ),    

    #block-003: maxpool + double conv 128->256
    to_Pool(         
        name="pool_b4", 
        offset="(1,0,0)", 
        to="(ccr_b4-east)",  
        width=1,         
        height=32 - 24, 
        depth=32 - 24, 
        opacity=0.5, 
        ),

    # arrow
    to_connection( 
        # "pool_b3"
        "ccr_b4",
        "pool_b4"
        ),
    # ],


    #Bottleneck
    #block-005
    to_ConvConvRelu( 
        name='ccr_b5', 
        s_filer=16, 
        n_filer=(512,512), 
        offset="(0,0,0)", 
        to="(pool_b4-east)", ##############
        width=(8,8), height=8, depth=8, caption="Bottleneck"  ),

    # to_connection( "pool_b4", "ccr_b5"),



    #Decoder
    *block_Unconv( 
        name="b6", 
        botton="ccr_b5", 
        top='end_b6', 
        s_filer=32,  
        n_filer=256, 
        offset="(1,0,0)", size=(16,16,5.0), opacity=0.5 ),

    # to_skip( of='ccr_b4', to='ccr_res_b6', pos=1.25),

    # # [
    #     to_UnPool(  
    #         name='unpool_{}'.format(name),    
    #         offset=offset,    
    #         to="({}-east)".format(botton),         
    #         width=1,              
    #         height=size[0],       
    #         depth=size[1], 
    #         opacity=opacity 
    #         ),
    #     to_ConvRes( 
    #         name='ccr_res_{}'.format(name),   
    #         offset="(0,0,0)", to="(unpool_{}-east)".format(name),    
    #         s_filer=str(s_filer), 
    #         n_filer=str(n_filer), 
    #         width=size[2], 
    #         height=size[0], 
    #         depth=size[1], 
    #         opacity=opacity 
    #         ),       
    #     to_Conv(    
    #         name='ccr_{}'.format(name),       
    #         offset="(0,0,0)", 
    #         to="(ccr_res_{}-east)".format(name),   
    #         s_filer=str(s_filer), 
    #         n_filer=str(n_filer), 
    #         width=size[2], 
    #         height=size[0], 
    #         depth=size[1] 
    #         ),
    #     to_ConvRes( 
    #         name='ccr_res_c_{}'.format(name), 
    #         offset="(0,0,0)", 
    #         to="(ccr_{}-east)".format(name),       
    #         s_filer=str(s_filer), 
    #         n_filer=str(n_filer), 
    #         width=size[2], 
    #         height=size[0], 
    #         depth=size[1], 
    #         opacity=opacity 
    #         ),       
    #     to_Conv(    
    #         name='{}'.format(top),            
    #         offset="(0,0,0)", 
    #         to="(ccr_res_c_{}-east)".format(name), 
    #         s_filer=str(s_filer), 
    #         n_filer=str(n_filer), 
    #         width=size[2], 
    #         height=size[0], 
    #         depth=size[1] 
    #         ),
    #     to_connection( 
    #         "{}".format( botton ), 
    #         "unpool_{}".format( name ) 
    #         ),
    # # ]


    *block_Unconv( 
        name="b7", 
        botton="end_b6", 
        top='end_b7', 
        s_filer=64, 
        n_filer=128, 
        offset="(2.1,0,0)", size=(25,25,4.5), opacity=0.5 ),

    to_skip( of='ccr_b3', to='ccr_res_b7', pos=1.25),  

    *block_Unconv( 
        name="b8",
          botton="end_b7", 
          top='end_b8', 
          s_filer=128, 
          n_filer=64, 
          offset="(2.1,0,0)", size=(32,32,3.5), opacity=0.5 ),

    to_skip( of='ccr_b2', to='ccr_res_b8', pos=1.25),    
    


    *block_Unconv( 
        name="b9", 
        botton="end_b8", 
        top='end_b9', 
        s_filer=256,
        n_filer=32,  
        offset="(2.1,0,0)", size=(40,40,2.5), opacity=0.5 ),

    to_skip( of='ccr_b1', to='ccr_res_b9', pos=1.25),
    
    to_ConvSoftMax( 
        name="soft1", 
        s_filer=256, 
        offset="(0.75,0,0)", 
        to="(end_b9-east)",
        width=1, height=40, depth=40, caption="SOFT" ),
    to_connection( "end_b9", "soft1"),
     
    to_end() 
    ]


def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex' )

if __name__ == '__main__':
    main()
    
