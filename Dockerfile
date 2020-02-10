FROM pytorch/pytorch:1.4-cuda10.1-cudnn7-devel

# Install astro Python packages
RUN conda install torchvision ignite -c pytorch -y
RUN conda install astropy -y
RUN pip install spectral-cube

# Add the torch-geometric packages
RUN pip install torch-sparse torch-cluster torch-spline-conv torch-scatter
RUN pip install torch-geometric

