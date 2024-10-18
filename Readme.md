## Getting started in 30 seconds

### *Installing the package*

Typical usage
![alt text](./image/image.png)

```$  python  test.py -c ./scale.cfg```
You can use the cfg file to config the cache parameters

### *Peculiarity*

PLRU ,Random,DRRIP replacement
Direct mapping,Set associative,Full associative
No *unalign* support(data size:32bit,so addr must 4byte align)
L1Cache(write back,write through) and L2Cache(write back,write through inclusive) are supported

### *Todo*

- [X]  More Replacements
- [ ]  Access Latency and miss Latency
- [ ]  Add Memory Trace
- [ ]  Add Cache consistency
- [ ]  Add exclusive or non-inclusive Cache
- [ ]  More test to check the correctness
