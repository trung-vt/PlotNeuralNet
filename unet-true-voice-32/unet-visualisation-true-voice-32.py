
import sys
sys.path.append('../')
from pycore.tikzeng import *
from pycore.blocks  import *

def get_double_conv(
        name: str,
        size: int,
        channels: int,
        display_size: int,
        actual_width_channels: int,
):
    return [
    # #block-000: double conv only 1->32
        to_Conv(
            name=f'ccr_{name}a', ###############
            s_filer=size, 
            n_filer=channels, 
            offset="(0,0,0)", 
            to="(0,0,0)", 
            width=actual_width_channels, 
            height=display_size, depth=display_size  ),
        to_Conv(
            name=f'ccr_{name}b', ###############
            s_filer=size, 
            n_filer=channels, 
            offset="(1,0,0)", 
            to=f"(ccr_{name}a-east)", 
            width=actual_width_channels, 
            height=display_size, depth=display_size  ),
    ]

arch = [ 
    to_head('..'), 
    to_cor(),
    to_begin(),
    
    #input
    # to_input( '../examples/fcn8s/cats.jpg', width=8, height=8),
    to_input( '../examples/noisy.png', width=8, height=8),


    # # #block-000: double conv only 1->32
    *get_double_conv(name="b1", size=256, channels=32, display_size=40, display_width_channels=2),
    

    #block-001: maxpool + double conv 32->64
    to_Pool(
        name="pool_b1", ##############
        # offset="(-0.6,-8,-0.6)", 
        offset="(0, -5, 0)", 
        # to="(ccr_b1-east)", #################
        # to="(ccr_b1a-east)", #################
        to="(ccr_b1b-southwest)", #################
        width=2, 
        height=20, depth=20, opacity=0.5),
    
    # #arrow
    to_connection_vertical( "ccr_b1b", "pool_b1"),

    to_ConvConvRelu( 
        name="ccr_b2",
        s_filer=str(128), 
        n_filer=(64,64), 
        offset="(0,0,0)", 
        to="(pool_b1-east)", 
        width=(4, 4), 
        height=20, 
        depth=20,   
        ),    


    #block-002: maxpool + double conv 64->128
    to_Pool(         
        name="pool_b2", 
        offset="(0,-4.5,0)", 
        to="(ccr_b2-east)",  
        width=4,         
        height=10, 
        depth=10, 
        opacity=0.5, 
        ),

    # # arrow
    # to_connection( 
    #     # "pool_b1", 
    #     "ccr_b2",
    #     "pool_b2"
    #     ),
    # # ],

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
        # to="(pool_b2-east)", 
        to="(pool_b2-east)", 
        width=(12, 12), 
        height=10, 
        depth=10,   
        ),    

    # arrow
    to_connection( 
        # "pool_b1", 
        "ccr_b2",
        # "pool_b2"
        "ccr_b3"
        ),
    # ],

    #block-003: maxpool + double conv 128->256
    to_Pool(         
        name="pool_b3", 
        offset="(1,0,0)", 
        to="(ccr_b3-east)",  
        width=1,         
        height=5, 
        depth=5, 
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
        width=(18, 18), 
        height=5, 
        depth=5,   
        ),    

    # #block-003: maxpool + double conv 128->256
    # to_Pool(         
    #     name="pool_b4", 
    #     offset="(0.5,0,0)", 
    #     to="(ccr_b4-east)",  
    #     width=1,         
    #     height=32 - 24, 
    #     depth=32 - 24, 
    #     opacity=0.5, 
    #     ),

    # # arrow
    # to_connection( 
    #     # "pool_b3"
    #     "ccr_b4",
    #     "pool_b4"
    #     ),
    # # ],


    # #Bottleneck
    # #block-005
    # to_ConvConvRelu( 
    #     name='ccr_b5', 
    #     s_filer=16, 
    #     n_filer=(512,512), 
    #     offset="(0,0,0)", 
    #     to="(pool_b4-east)", ##############
    #     width=(8,8), height=8, depth=8, caption="Bottleneck"  ),

    # # to_connection( "pool_b4", "ccr_b5"),



    # #Decoder
    # *block_Unconv( 
    #     name="b6", 
    #     botton="ccr_b5", 
    #     top='end_b6', 
    #     s_filer=32,  
    #     n_filer=256, 
    #     offset="(1,0,0)", size=(16,16,5.0), opacity=0.5 ),

    # to_skip( of='ccr_b4', to='ccr_res_b6', pos=1.25),

    # # # [
    #     to_UnPool(  
    #         name='unpool_b6',    
    #         offset="(1,0,0)",    
    #         # to="(ccr_b5-east)",         
    #         to="(ccr_b4-east)",         
    #         width=1,              
    #         height=16,       
    #         depth=16, 
    #         opacity=0.5 
    #         ),
    #     to_ConvRes( 
    #         name='ccr_res_b6',   
    #         offset="(0,0,0)", 
    #         to="(unpool_b6-east)",    
    #         s_filer=str(32), 
    #         n_filer=str(256), 
    #         width=5.0, 
    #         height=16, 
    #         depth=16, 
    #         opacity=0.5 
    #         ),       
    #     to_Conv(    
    #         name='ccr_b6',       
    #         offset="(0,0,0)", 
    #         to="(ccr_res_b6-east)",   
    #         s_filer=str(32), 
    #         n_filer=str(256), 
    #         width=5.0, 
    #         height=16, 
    #         depth=16
    #         ),
    #     to_ConvRes( 
    #         name='ccr_res_c_b6', 
    #         offset="(0,0,0)", 
    #         to="(ccr_b6-east)",       
    #         s_filer=str(32), 
    #         n_filer=str(256), 
    #         width=5.0, 
    #         height=16, 
    #         depth=16,
    #         opacity=0.5 
    #         ),       
    #     to_Conv(    
    #         name='end_b6',            
    #         offset="(0,0,0)", 
    #         to="(ccr_res_c_b6-east)", 
    #         s_filer=str(32), 
    #         n_filer=str(256), 
    #         width=5.0, 
    #         height=16, 
    #         depth=16
    #         ),
    #     to_connection( 
    #         # "ccr_b5", 
    #         "ccr_b4", 
    #         "unpool_b6"
    #         ),
    # # # ]


    # *block_Unconv( 
    #     name="b7", 
    #     botton="end_b6", 
    #     top='end_b7', 
    #     s_filer=64, 
    #     n_filer=128, 
    #     offset="(2.1,0,0)", size=(25,25,4.5), opacity=0.5 ),

    # # [
        to_UnPool(  
            name='unpool_b7',    
            offset="(1,0,0)",    
            # to="(ccr_b6-east)",         
            to="(ccr_b4-east)",         
            # to="(end_b6-east)",         
            width=1,              
            height=10,       
            depth=10, 
            opacity=0.5 
            ),
        to_ConvRes( 
            name='ccr_res_b7',   
            offset="(0,0,0)", 
            to="(unpool_b7-east)",    
            s_filer=str(64), 
            n_filer=str(128), 
            width=6, 
            height=10, 
            depth=10, 
            opacity=0.5 
            ),       
        to_Conv(    
            name='ccr_b7',       
            offset="(0,0,0)", 
            to="(ccr_res_b7-east)",   
            s_filer=str(64), 
            n_filer=str(128), 
            width=6, 
            height=10, 
            depth=10
            ),
        to_ConvRes( 
            name='ccr_res_c_b7', 
            offset="(0,0,0)", 
            to="(ccr_b7-east)",       
            s_filer=str(64), 
            n_filer=str(128), 
            width=6, 
            height=10, 
            depth=10,
            opacity=0.5 
            ),       
        to_Conv(    
            name='end_b7',            
            offset="(0,0,0)", 
            to="(ccr_res_c_b7-east)", 
            s_filer=str(64), 
            n_filer=str(128), 
            width=6, 
            height=10, 
            depth=10
            ),
        to_connection( 
            # "ccr_b6",
            "ccr_b4",
            # "end_b6", 
            "unpool_b7"
            ),
    # # ]


    to_skip( of='ccr_b3', to='ccr_res_b7', pos=1.25),  


    # *block_Unconv( 
    #     name="b8",
    #       botton="end_b7", 
    #       top='end_b8', 
    #       s_filer=128, 
    #       n_filer=64, 
    #       offset="(2.1,0,0)", size=(32,32,3.5), opacity=0.5 ),

    # # [
        to_UnPool(  
            name='unpool_b8',    
            offset="(0,4.5,0)",    
            # to="(ccr_b7-east)",         
            to="(end_b7-east)",         
            width=1,              
            height=20,       
            depth=20, 
            opacity=0.5 
            ),
        to_ConvRes( 
            name='ccr_res_b8',   
            offset="(0,0,0)", 
            to="(unpool_b8-east)",    
            s_filer=str(128), 
            n_filer=str(64), 
            width=5, 
            height=20, 
            depth=20, 
            opacity=0.5 
            ),       
        to_Conv(    
            name='ccr_b8',       
            offset="(0,0,0)", 
            to="(ccr_res_b8-east)",   
            s_filer=str(128), 
            n_filer=str(64), 
            width=5, 
            height=20, 
            depth=20
            ),
        to_ConvRes( 
            name='ccr_res_c_b8', 
            offset="(0,0,0)", 
            to="(ccr_b8-east)",       
            s_filer=str(128), 
            n_filer=str(64), 
            width=5, 
            height=20, 
            depth=20,
            opacity=0.5 
            ),       
        to_Conv(    
            name='end_b8',            
            offset="(0,0,0)", 
            to="(ccr_res_c_b8-east)", 
            s_filer=str(128), 
            n_filer=str(64), 
            width=5, 
            height=20, 
            depth=20
            ),
        to_connection( 
            # "ccr_b7",
            "end_b7", 
            "unpool_b8"
            ),
    # # ]

    to_skip( of='ccr_b2', to='ccr_res_b8', pos=1.25),    
    


    # *block_Unconv( 
    #     name="b9", 
    #     botton="end_b8", 
    #     top='end_b9', 
    #     s_filer=256,
    #     n_filer=32,  
    #     offset="(2.1,0,0)", size=(40,40,2.5), opacity=0.5 ),

    # # [
        to_UnPool(  
            name='unpool_b9',    
            offset="(0,8,0)",    
            # to="(ccr_b8-east)",         
            to="(end_b8-east)",         
            width=1,              
            height=16 + 24,       
            depth=16 + 24, 
            opacity=0.5 
            ),
        to_ConvRes( 
            name='ccr_res_b9',   
            offset="(0,0,0)", 
            to="(unpool_b9-east)",    
            s_filer=str(256), 
            n_filer=str(32), 
            width=3, 
            height=16 + 24, 
            depth=16 + 24, 
            opacity=0.5 
            ),       
        to_Conv(    
            name='ccr_b9',       
            offset="(0,0,0)", 
            to="(ccr_res_b9-east)",   
            s_filer=str(256), 
            n_filer=str(32), 
            width=3, 
            height=16 + 24, 
            depth=16 + 24
            ),
        to_ConvRes( 
            name='ccr_res_c_b9', 
            offset="(0,0,0)", 
            to="(ccr_b9-east)",       
            s_filer=str(256), 
            n_filer=str(32), 
            width=3, 
            height=16 + 24, 
            depth=16 + 24,
            opacity=0.5 
            ),       
        to_Conv(    
            name='end_b9',            
            offset="(0,0,0)", 
            to="(ccr_res_c_b9-east)", 
            s_filer=str(256), 
            n_filer=str(32), 
            width=3, 
            height=16 + 24, 
            depth=16 + 24
            ),
        to_connection( 
            # "ccr_b8",
            "end_b8", 
            "unpool_b9"
            ),
    # # ]

    to_skip( of='ccr_b1b', to='ccr_res_b9', pos=1.25),
    
    to_ConvSoftMax( 
        name="soft1", 
        s_filer=256, 
        offset="(0.75,0,0)", 
        to="(end_b9-east)",
        width=1, height=40, depth=40, 
        # caption="SOFT" 
        # caption="MSE"
        ),

    to_connection( "end_b9", "soft1"),

    # to_input( '../examples/fcn8s/cats.jpg', width=8, height=8),
     
    to_end() 
    ]


def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex' )

if __name__ == '__main__':
    main()
    
