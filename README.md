"Alpaka" is a communicator between user space and kernel (and vice versa). E.g. it creates a message defined by a user/developer with a specific parameters that Kernel module(s) expected to understand.

### How to Install

#### PIP

```
  sudo apt install python3-pip
  git clone git@github.hpe.com:atsugami-kun/python3-alpaka.git

  cd ./python3-alpaka
  pip3 install -r requirements.txt
```


### How to Use

Create a class and inherite from [alpaka.Zookeeper](https://github.hpe.com/atsugami-kun/python3-alpaka/blob/master/alpaka/zookeeper.py). Then, override "build_msg(self, \*\*kwargs)" function and use the object as follows:

```
    zoo = Journal.mainapp.zookeeper
    msg = zoo.build_msg(cmd=zoo.cfg.get('ADD'), arg_one="some value", arg_two="other value", anything_else="yet another")
    
    retval = zoo.sendmsg(msg)
```

[Example as used by LLaMaS](https://github.hpe.com/atsugami-kun/llamas/blob/master/llamas/blueprints/device/blueprint.py)
