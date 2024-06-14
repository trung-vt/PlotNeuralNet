
import sys
sys.path.append('../')
from pycore.tikzeng import *
from pycore.blocks  import *

N_DIM = 2

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
        n_dim=N_DIM,
    ),

    # block-001: maxpool + double conv 32->64
    *get_encoder_block(
        block_num=2,
        offset="(0, -3, 0)", relative_to="ccr_b1", direction="southwest",
        feature_map_size=128, n_channels=64,
        feature_map_size_display=20,
        n_in_channels_display=2,
        n_out_channels_display=4,
        n_dim=N_DIM,
    ),

    # block-002: maxpool + double conv 64->128
    *get_encoder_block(
        block_num=3,
        offset="(0, -3, 0)", relative_to="ccr_b2", direction="southwest",
        feature_map_size=64, n_channels=128,
        feature_map_size_display=10,
        n_in_channels_display=4,
        n_out_channels_display=8,
        n_dim=N_DIM,
    ),

    # block-003: maxpool + double conv 128->256
    *get_encoder_block(
        block_num=4,
        offset="(0, -2, 0)", relative_to="ccr_b3", direction="southwest",
        feature_map_size=32, n_channels=256,
        feature_map_size_display=5,
        n_in_channels_display=8,
        n_out_channels_display=16,
        n_dim=N_DIM,
    ),

    
    *get_decoder_block(
        block_num=7, encoder_block_num=3,
        offset="(0, 2.5, 0)", relative_to="ccr_b4", direction="northwest",
        feature_map_size=64, n_channels=128,
        n_encoder_channels_display=8,
        n_out_channels_display=8,
        feature_map_size_display=10,
        n_dim=N_DIM,
    ),

    *get_decoder_block(
        block_num=8, encoder_block_num=2,
        offset="(0, 4, 0)", relative_to="ccr_b7", direction="northwest",
        feature_map_size=128, n_channels=64,
        n_encoder_channels_display=4,
        n_out_channels_display=4,
        feature_map_size_display=20,
        n_dim=N_DIM,
    ),

    *get_decoder_block(
        block_num=9, encoder_block_num=1,
        offset="(0, 5, 0)", relative_to="ccr_b8", direction="northwest",
        feature_map_size=256, n_channels=32,
        n_encoder_channels_display=2,
        n_out_channels_display=2,
        feature_map_size_display=40,
        n_dim=N_DIM,
    ),


    to_ConvSoftMax( 
        name="soft1", 
        s_filer=256, 
        offset="(0.75, 0, 0)", 
        # to="(end_b9-east)",
        to="(ccr_b9-east)",
        width=1, height=40, 
        # depth=40, 
        depth=0, 
        # caption="SOFT" 
        # caption="MSE"
        ),

    # to_connection( "end_b9", "soft1"),
    to_connection( "ccr_b9", "soft1"),

    # to_input( '../examples/fcn8s/cats.jpg', width=8, height=8),
     
    to_end() 
    ]


def main():
    namefile = str(sys.argv[0]).split('.')[0]
    to_generate(arch, namefile + '.tex' )

if __name__ == '__main__':
    main()
    
