## 1. Set up the environment

### Tools

#### Eclipse IDE
Download the C/C++ edition of the Eclipse IDE (Version: 2020-09 (4.17.0)).

#### PyDev Plugin

Use Eclipse Marketplace to find and install PyDev (8.0.0.202009061309).

#### git
```bash
sudo zypper install git         # 2.26.2
```

#### python

```
sudo zypper install python3	     # 3.6.10
```

#### avrdude

```
sudo zypper install avrdude      # 6.3  (include libftdi1)
```





### Dependencies

#### Python modules
```bash
sudo zypper install -y python3-pyserial python3-opengl python3-pyglet python3-numpy python3-scipy python3-matplotlib python3-wxPython
```









#### Custom OpenCV

```bash
sudo zypper remove python3-opencv  # first remove previous versions of opencv
```

Now clone the custom version of it.

```
git clone git@github.com:bq/opencv.git
```



*** GOT HERE ***



#### Figure out which Arduino ports are mapped to which Zum-board components.Video 4 Linux

```bash
sudo apt-get install v4l-utils
```

In order to generate Debian and Windows packages, some extra dependencies are needed

#### Packaging dependencies
```bash
sudo apt-get install build-essential pkg-config python-dev python-stdeb p7zip-full curl nsis
```

## 2. Download source code

All source code is available on GitHub. You can download main Horus project by doing:

### Horus
```bash
git clone https://github.com/bq/horus.git
```
or
```bash
git clone git@github.com:bq/horus.git
```

### Custom OpenCV

Several improvements and optimizations have been made in GNU/Linux version of OpenCV libraries. If you want to contribute to this custom version, you can download it from:

```bash
git clone https://github.com/bq/opencv.git
```
or
```bash
git clone git@github.com:bq/opencv.git
```

And build it your own: [instructions](https://github.com/bqlabs/opencv/wiki/Build)

## 3. Execute source code

In the project directory, execute the command:

```bash
./horus
```

### Unit testing

To run the tests install nose:

```bash
sudo -H pip install -U nose
```

And execute:

```bash
nosetests test
```

## 4. Build packages

Horus development comes with a script *package.sh*. This script generates a final release package. You should not need it during development, unless you are changing the release process. If you want to distribute your own version of Horus, then the *packaFigure out which Arduino ports are mapped to which Zum-board components.ge.sh* script will allow you to do that.

### Version
```bash
bash package.sh version  # Generate version file
```

### GNU/Linux UbuntuFor older ubuntu versions
￼
sudo apt-get install python-wxgtk2.8
For newer ubuntu versions

```bash
bash package.sh debian     # Generate deb package
bash package.sh debian -s  # Generate sources
bash package.sh debian -i  # Install deb package
bash package.sh debian -u  # Upload to launchpad
```

### Windows
```bash
bash package.sh win32        # Generate exe package
bash package.sh win32 /path  # Generate exe using /path for deps
```
