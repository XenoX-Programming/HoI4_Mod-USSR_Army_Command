#!/usr/bin/env python3
"""Convert ColorfulSoft's ChromaGAN half-precision weight shards to ONNX.

This is a colorization-only network: it predicts two chroma channels from the
source luminance. It does not synthesize a replacement face or photograph.
Weights are development assets and are not redistributed in the mod.
"""
from pathlib import Path
import numpy as np
import onnx
from onnx import helper, numpy_helper, TensorProto

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEIGHTS = Path('/home/user/.cache/hoi4-assets/chromagan')
OUT = Path('/home/user/.cache/hoi4-assets/chromagan.onnx')

class Reader:
    def __init__(self, folder):
        self.data = b''.join((Path(folder)/f'{i}.bin').read_bytes() for i in range(4))
        self.pos = 0
    def take(self, n):
        b = self.data[self.pos:self.pos+n*2]
        if len(b) != n*2:
            raise ValueError('weight shard truncated')
        self.pos += n*2
        return np.frombuffer(b, dtype='<f2').astype(np.float32)
    def weights(self, k, cin, cout):
        # Data.cs LoadWeights loops filter, input-channel, row, column: OIHW.
        return self.take(k*k*cin*cout).reshape(cout,cin,k,k).copy()
    def bias(self, n):
        return self.take(n)

def build(folder):
    r = Reader(folder)
    nodes, init = [], []
    def const(name, arr):
        arr = np.asarray(arr)
        if arr.dtype.kind not in 'fi':
            arr = arr.astype(np.int64)
        init.append(numpy_helper.from_array(arr.astype(np.float32) if arr.dtype.kind == 'f' else arr.astype(np.int64), name))
        return name
    def conv(name, x, k, cin, cout, stride=1):
        w = const(name+'_w', r.weights(k,cin,cout))
        b = const(name+'_b', r.bias(cout))
        y = name+'_y'
        nodes.append(helper.make_node('Conv',[x,w,b],[y],kernel_shape=[k,k],strides=[stride,stride],pads=[k//2,k//2,k//2,k//2]))
        return y
    def relu(x):
        y = x+'_relu'; nodes.append(helper.make_node('Relu',[x],[y])); return y
    def pool(x):
        y = x+'_pool'; nodes.append(helper.make_node('MaxPool',[x],[y],kernel_shape=[2,2],strides=[2,2])); return y
    def bn(name,x,n):
        mean=const(name+'_mean',r.bias(n)); var=const(name+'_var',r.bias(n)); beta=const(name+'_beta',r.bias(n)); gamma=const(name+'_gamma',r.bias(n))
        y=name+'_y'; nodes.append(helper.make_node('BatchNormalization',[x,gamma,beta,mean,var],[y],epsilon=1e-5)); return y
    def dense(name,x,cin,cout):
        # LoadWeights(1,1,cin,cout) stores output-major rows; Gemm needs transB.
        w=const(name+'_w',r.take(cin*cout).reshape(cout,cin)); b=const(name+'_b',r.bias(cout)); y=name+'_y'
        nodes.append(helper.make_node('Gemm',[x,w,b],[y],alpha=1.0,beta=1.0,transA=0,transB=1)); return y
    def up(x):
        scales=const(x+'_scales',np.array([1,1,2,2],dtype=np.float32)); y=x+'_up'
        nodes.append(helper.make_node('Resize',[x,'',scales],[y],mode='nearest',coordinate_transformation_mode='asymmetric',nearest_mode='floor')); return y
    x='input'
    for i,(k,ci,co) in enumerate([(3,3,64),(3,64,64),(3,64,128),(3,128,128),(3,128,256),(3,256,256),(3,256,256),(3,256,512),(3,512,512),(3,512,512)],1):
        x=relu(conv(f'vgg{i}',x,k,ci,co))
        if i in (2,4,7): x=pool(x)
    mid=x
    g=x
    for i,(k,ci,co,st) in enumerate([(3,512,512,2),(3,512,512,1),(3,512,512,2),(3,512,512,1)],1):
        g=bn(f'global_bn{i}',relu(conv(f'global{i}',g,k,ci,co,st)),co)
    # C# Dense loops channel-major, then row, then column: CHW flatten.
    g_flat='global_flat'; nodes.append(helper.make_node('Flatten',[g],[g_flat],axis=1))
    g_flat=dense('dense1',g_flat,25088,1024)
    g_flat=dense('dense2',g_flat,1024,512)
    g_flat=dense('dense3',g_flat,512,256)
    g_vec='global_vec'; nodes.append(helper.make_node('Reshape',[g_flat,const('global_shape',np.array([1,256,1,1],dtype=np.int64))],[g_vec]))
    # Broadcast global context over the 28x28 mid-level map.
    g_map='global_map'; nodes.append(helper.make_node('Expand',[g_vec,const('mid_shape',np.array([1,256,28,28],dtype=np.int64))],[g_map]))
    mid=bn('mid_bn1',relu(conv('mid1',mid,3,512,512)),512)
    mid=bn('mid_bn2',relu(conv('mid2',mid,3,512,256)),256)
    x='fused'; nodes.append(helper.make_node('Concat',[mid,g_map],[x],axis=1))
    x=relu(conv('out1',x,1,512,256))
    x=relu(conv('out2',x,3,256,128)); x=up(x)
    x=relu(conv('out3',x,3,128,64))
    x=relu(conv('out4',x,3,64,64)); x=up(x)
    x=relu(conv('out5',x,3,64,32))
    x=conv('out6',x,3,32,2)
    nodes.append(helper.make_node('Sigmoid',[x],['chroma_sigmoid']))
    x='output'; nodes.append(helper.make_node('Resize',['chroma_sigmoid','',const('out_scales',np.array([1,1,2,2],dtype=np.float32))],[x],mode='nearest',coordinate_transformation_mode='asymmetric',nearest_mode='floor'))
    if r.pos != len(r.data):
        raise ValueError(f'weight reader mismatch: {r.pos} != {len(r.data)}')
    graph=helper.make_graph(nodes,'ChromaGAN-colorization',[helper.make_tensor_value_info('input',TensorProto.FLOAT,[1,3,224,224])],[helper.make_tensor_value_info('output',TensorProto.FLOAT,[1,2,224,224])],init)
    model=helper.make_model(graph,opset_imports=[helper.make_opsetid('',13)])
    model.ir_version=8
    onnx.checker.check_model(model)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    onnx.save(model,OUT)
    print(OUT, OUT.stat().st_size)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--weights',type=Path,default=DEFAULT_WEIGHTS)
    a=p.parse_args(); build(a.weights)
