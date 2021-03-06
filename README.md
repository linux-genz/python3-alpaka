"Alpaka" is a communicator between user space and kernel (and vice versa). E.g. it creates a message defined by a user/developer with a specific parameters that Kernel module(s) expected to understand.

### How to Install

#### PIP

```
  sudo apt install python3-pip
  pip3 git+https://github.com/linux-genz/python3-alpaka.git@v0.1
```


### How to Use

Create a class and inherite from [alpaka.Messenger](https://github.com/linux-genz/python3-alpaka/blob/master/alpaka/messenger.py). Then, override "build_msg(self, \*\*kwargs)" function and use the object as follows:

```
    zoo = Journal.mainapp.zookeeper
    msg = zoo.build_msg(cmd=zoo.cfg.get('ADD'), arg_one="some value", arg_two="other value", anything_else="yet another")

    retval = zoo.sendmsg(msg)
```

[Example as used by LLaMaS](https://github.com/linux-genz/llamas/blob/master/llamas/blueprints/device/blueprint.py)
