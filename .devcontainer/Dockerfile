### Build environment ###
FROM python:3.8-slim-buster AS builder

COPY requirements-build.txt /usr/src
COPY checksums /usr/src

# add build user
RUN useradd --uid 1000 -m build 

# install dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get -q update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q install -y wget git build-essential cmake pkg-config libsuitesparse-dev libgl1-mesa-dev libglew-dev \
    && DEBIAN_FRONTEND=noninteractive apt-get -q clean

# Build dependencies
RUN cd /home/build \
    && su -c '\
    wget -nv "https://gitlab.com/libeigen/eigen/-/archive/3.3.4/eigen-3.3.4.tar.gz" \
    && sha256sum -c /usr/src/checksums \
    && tar -xf eigen-3.3.4.tar.gz \
    && rm eigen-3.3.4.tar.gz \
    && cd eigen-3.3.4 \
    && mkdir build \
    && cd build \
    && cmake ..' build \
    && cd eigen-3.3.4/build \
    && make install \
    && cd ../.. \
    && su -c '\
    rm -R eigen-3.3.4 \
    && mkdir lib \
    && pip install --no-cache-dir -r /usr/src/requirements-build.txt \
    && git clone --single-branch --branch master "https://github.com/uoip/g2opy.git" \
    && cd g2opy \
    && git reset --hard 5587024b17fd812c66d91740716fbf0bf5824fbc \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j4 \
    && cd ~ \
    && mv g2opy/lib/g2o.cpython-38-x86_64-linux-gnu.so lib/ \
    && rm -Rf g2opy \
    && git clone --single-branch --branch master "https://github.com/stevenlovegrove/Pangolin.git" \
    && cd Pangolin \
    && git reset --hard 86eb4975fc4fc8b5d92148c2e370045ae9bf9f5d \
    && git submodule init \
    && git submodule update \
    && mkdir build \
    && cd build \
    && cmake .. \
    && cmake --build . \
    && cd ~ \
    && mv Pangolin/build/src/pypangolin.cpython-38-x86_64-linux-gnu.so lib/ \
    && mv Pangolin/build/src/libpangolin.so lib/ \
    && rm -Rf Pangolin' build

### Runtime environment ###
FROM python:3.8-slim-buster

RUN useradd --uid 1000 -m app \
    && mkdir -p /opt/app/lib \
    && DEBIAN_FRONTEND=noninteractive apt-get -q update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q install -y libgl1 libglib2.0-0 libsuitesparse-dev libglu1-mesa libglew2.1 libopengl0 libsm6 libice6 git \
    && DEBIAN_FRONTEND=noninteractive apt-get -q clean

# Copy native dependencies from our build environment
COPY --from=builder --chown=root:root /home/build/lib/g2o.cpython-38-x86_64-linux-gnu.so /opt/app/lib/
COPY --from=builder --chown=root:root /home/build/lib/pypangolin.cpython-38-x86_64-linux-gnu.so /opt/app/lib/
COPY --from=builder --chown=root:root /home/build/lib/libpangolin.so /usr/local/lib/

# Update ld cache so it will find libpangolin.so
RUN ldconfig
