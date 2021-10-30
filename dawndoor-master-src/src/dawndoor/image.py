from framebuf import MONO_HLSB, FrameBuffer


PBM_ASCII = 'P1'
PBM_BINARY = 'P4'


def load_pbm(fname):
    """Loads a PBM file into a FrameBuffer object"""
    with open(fname, 'rb') as pbm_file:
        _ = pbm_file.readline()
        _ = pbm_file.readline()
        width, height = tuple([int(val) for val in pbm_file.readline().split(b' ')])
        data = bytearray(pbm_file.read())
    return FrameBuffer(data, width, height, MONO_HLSB)
