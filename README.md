#EMD
Earth mover's distance on Nvidia GPUs

##CUDA
CUDA and relevant NVIDIA drivers have to be installed from their site. This should be done first.

##Building
To build, you must install stack with
```
wget -qO- https://get.haskellstack.org/ | sh
```
Then type `stack setup` followed by `stack build`

The script `start.sh` will create common points between python and haskell. 

Once this is done `cd` into `haskellemd` and run
```
sudo python3 setup.py install
```

After this, the haskemd module can be used from any directory.

##Python
The provided python wrapper takes two (one-dimensional) numpy arrays and computes the EMD:
```
python3
>>>import haskemd
>>>haskemd.emd(haskemd.sinksrand(1024), haskemd.sourcesrand(1024))
692959.0
```
`sinksrand(1024)` and `sourcesrand(1024)` just generates test data with 1024 bins. 

To try your own, consider the following example:
```
>>>import haskemd
>>>import numpy as np
>>>a1 = np.array([1,2,3,4])
>>>a2 = np.array([4,3,2,1])
>>>haskemd(a1, a2)
6.0
```

##Ground distance
In our case, the "ground distance" is the hamming distance. Moreover, the matrix for the metric is automatically generated. This means that an array like
```
np.array([0.25,0.5])
```
must have the correct values in the correct places. In fact, d\_ij is based on the indices. Here, d\_01 would mean the distance between the bin containing 0.25 and the bin containing 0.5

##Hamming distance
To get the hamming distance from a integer indices, say 3 and 7, we first convert to binary to get 011 and 111. Then we can compute the hamming distance to get 1 (in this case).
