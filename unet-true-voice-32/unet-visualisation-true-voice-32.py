
import sys
sys.path.append('../')
from pycore.tikzeng import *
from pycore.blocks  import *

def get_double_conv(
        name: str,
        offset: str, relative_to: str,
        feature_map_size: int, n_channels: int,
        feature_map_size_display: int,
        n_channels_display: int,
        n_dim: int = 2,
):
    if n_dim == 2: depth_display = 0
    elif n_dim == 3: depth_display = feature_map_size_display
    else: raise ValueError(f"n_dim must be 2 or 3, but got {n_dim}")
    
    block_a = f"ccr_{name}a"
    block_last = f"ccr_{name}"
    b_to_a_offset = "(0.5, 0, 0)"

    return [
        to_Conv(
            name=block_a, ###############
            offset=offset, 
            to=relative_to, 
            s_filer=feature_map_size, n_filer=n_channels, 
            width=n_channels_display, height=feature_map_size_display, depth=depth_display 
        ),
        to_Conv(
            name=block_last, ###############
            offset=b_to_a_offset, 
            to=f"({block_a}-east)", 
            s_filer=feature_map_size, n_filer=n_channels, 
            width=n_channels_display, height=feature_map_size_display, depth=depth_display
        ),
        to_connection(block_a, block_last),
    ]


def get_encoder_block(
        block_num: int,
        offset: str, relative_to: str, direction: str,
        feature_map_size: int, n_channels: int,
        feature_map_size_display: int,
        n_in_channels_display: int,
        n_out_channels_display: int,
        n_dim: int = 2,
):
    if n_dim == 2:
        pool_depth = 0
    elif n_dim == 3:
        pool_depth = feature_map_size_display
    else:
        raise ValueError(f"n_dim must be 2 or 3, but got {n_dim}")

    pool_name = f"pool_b{block_num}"

    return [
        to_Pool(
            name=pool_name, ##############
            offset=offset, 
            to=f"({relative_to}-{direction})",
            width=n_in_channels_display, 
            height=feature_map_size_display, 
            depth=pool_depth, 
            opacity=0.5
        ),
        # to_connection_vertical( relative_to, pool_name),
        arrow(f"{relative_to}-southwest", f"{pool_name}-northwest"),
        *get_double_conv(
            name=f"b{block_num}",
            offset="(0.5, 0, 0)",
            relative_to=f"(pool_b{block_num}-east)",
            feature_map_size=feature_map_size,
            n_channels=n_channels,
            feature_map_size_display=feature_map_size_display,
            n_channels_display=n_out_channels_display,
            n_dim=n_dim,
        ),
        to_connection(pool_name, f"ccr_b{block_num}a"), 
    ] 


def get_decoder_block(
        block_num: int, encoder_block_num: int,
        offset: str, relative_to: str, direction: str,
        feature_map_size: int, n_channels: int,
        feature_map_size_display: int,
        n_encoder_channels_display: int,
        n_out_channels_display: int,
        n_dim: int = 2,
):
    if n_dim == 2:
        depth = 0
    elif n_dim == 3:
        depth = 10
    else:
        raise ValueError(f"n_dim must be 2 or 3, but got {n_dim}")
    return [
        to_UnPool(  
            name=f'unpool_b{block_num}',    
            offset=offset,    
            to=f"({relative_to}-{direction})",         
            width=n_out_channels_display,              
            height=feature_map_size_display,       
            depth=depth, 
            opacity=0.5 
        ),
        arrow(f"{relative_to}-northwest", f"unpool_b{block_num}-southwest"),
        to_Conv(    
            name=f'ccr_res_b{block_num}',   
            offset="(0, 0, 0)", 
            to=f"(unpool_b{block_num}-east)",    
            s_filer=str(feature_map_size), 
            n_filer=str(n_channels), 
            width=n_encoder_channels_display, 
            height=feature_map_size_display, 
            depth=depth, 
        ),  
        to_skip( of=f'ccr_b{encoder_block_num}', to=f'ccr_res_b{block_num}', pos=1.25),  


        *get_double_conv(
            name=f"b{block_num}",
            offset="(0.5, 0, 0)",
            relative_to=f"(ccr_res_b{block_num}-east)",
            feature_map_size=feature_map_size,
            n_channels=n_channels,
            feature_map_size_display=feature_map_size_display,
            n_channels_display=n_out_channels_display,
            n_dim=n_dim,
        ),
        arrow(f"ccr_res_b{block_num}-east", f"ccr_b{block_num}a-west"),


        # to_Conv(    
        #     name=f'ccr_b{block_num}',       
        #     offset="(0.5, 0, 0)", 
        #     to=f"(ccr_res_b{block_num}-east)",   
        #     s_filer=str(feature_map_size), 
        #     n_filer=str(n_channels), 
        #     width=n_out_channels_display, 
        #     height=feature_map_size_display, 
        #     depth=depth
        # ),
        # to_Conv(    
        #     name=f'end_b{block_num}',            
        #     offset="(0.5, 0, 0)", 
        #     # to=f"(ccr_res_c_b{block_num}-east)", 
        #     to=f"(ccr_b{block_num}-east)", 
        #     s_filer=str(feature_map_size), 
        #     n_filer=str(n_channels), 
        #     width=n_out_channels_display, 
        #     height=feature_map_size_display, 
        #     depth=depth
        # ),
    ]


arch = [ 
    to_head('..'), 
    to_cor(),
    to_begin(),
    
    # input
    to_input( '../examples/noisy.png', width=8, height=8),

    # block-000: double conv only 1->32
    *get_double_conv(
        name="b1",
        offset="(0,0,0)",
        relative_to="(0,0,0)",
        feature_map_size=256,
        n_channels=32,
        feature_map_size_display=40,
        n_channels_display=2,
        n_dim=2,
    ),

    # block-001: maxpool + double conv 32->64
    *get_encoder_block(
        block_num=2,
        offset="(0, -5, 0)", relative_to="ccr_b1", direction="southwest",
        feature_map_size=128, n_channels=64,
        feature_map_size_display=20,
        n_in_channels_display=2,
        n_out_channels_display=4,
        n_dim=2,
    ),

    # block-002: maxpool + double conv 64->128
    *get_encoder_block(
        block_num=3,
        offset="(0, -3, 0)", relative_to="ccr_b2", direction="southwest",
        feature_map_size=64, n_channels=128,
        feature_map_size_display=10,
        n_in_channels_display=4,
        n_out_channels_display=8,
        n_dim=2,
    ),

    # block-003: maxpool + double conv 128->256
    *get_encoder_block(
        block_num=4,
        offset="(0, -2, 0)", relative_to="ccr_b3", direction="southwest",
        feature_map_size=32, n_channels=256,
        feature_map_size_display=5,
        n_in_channels_display=8,
        n_out_channels_display=16,
        n_dim=2,
    ),

    
    *get_decoder_block(
        block_num=7, encoder_block_num=3,
        offset="(0, 2.5, 0)", relative_to="ccr_b4", direction="northwest",
        feature_map_size=64, n_channels=128,
        n_encoder_channels_display=8,
        n_out_channels_display=8,
        feature_map_size_display=10,
        n_dim=2,
    ),

    *get_decoder_block(
        block_num=8, encoder_block_num=2,
        offset="(0, 4, 0)", relative_to="ccr_b7", direction="northwest",
        feature_map_size=128, n_channels=64,
        n_encoder_channels_display=4,
        n_out_channels_display=4,
        feature_map_size_display=20,
        n_dim=2,
    ),


    # *block_Unconv( 
    #     name="b8",
    #       botton="end_b7", 
    #       top='end_b8', 
    #       s_filer=128, 
    #       n_filer=64, 
    #       offset="(2.1,0,0)", size=(32,32,3.5), opacity=0.5 ),

    # # # [
    #     to_UnPool(  
    #         name='unpool_b8',    
    #         offset="(0,4.5,0)",    
    #         # to="(ccr_b7-east)",         
    #         to="(ccr_b7-east)",         
    #         # to="(end_b7-east)",         
    #         width=1,              
    #         height=20,       
    #         depth=20, 
    #         opacity=0.5 
    #         ),
    #     to_ConvRes( 
    #         name='ccr_res_b8',   
    #         offset="(0,0,0)", 
    #         to="(unpool_b8-east)",    
    #         s_filer=str(128), 
    #         n_filer=str(64), 
    #         width=5, 
    #         height=20, 
    #         depth=20, 
    #         opacity=0.5 
    #         ),       
    #     to_Conv(    
    #         name='ccr_b8',       
    #         offset="(0,0,0)", 
    #         to="(ccr_res_b8-east)",   
    #         s_filer=str(128), 
    #         n_filer=str(64), 
    #         width=5, 
    #         height=20, 
    #         depth=20
    #         ),
    #     to_ConvRes( 
    #         name='ccr_res_c_b8', 
    #         offset="(0,0,0)", 
    #         to="(ccr_b8-east)",       
    #         s_filer=str(128), 
    #         n_filer=str(64), 
    #         width=5, 
    #         height=20, 
    #         depth=20,
    #         opacity=0.5 
    #         ),       
    #     to_Conv(    
    #         name='end_b8',            
    #         offset="(0,0,0)", 
    #         to="(ccr_res_c_b8-east)", 
    #         s_filer=str(128), 
    #         n_filer=str(64), 
    #         width=5, 
    #         height=20, 
    #         depth=20
    #         ),
    #     to_connection( 
    #         "ccr_b7",
    #         # "end_b7", 
    #         "unpool_b8"
    #         ),
    # # # ]

    # to_skip( of='ccr_b2', to='ccr_res_b8', pos=1.25),    
    


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
            to="(ccr_b8-east)",         
            # to="(end_b8-east)",         
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
            "ccr_b8",
            # "end_b8", 
            "unpool_b9"
            ),
    # # ]

    to_skip( of='ccr_b1', to='ccr_res_b9', pos=1.25),
    
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
    
