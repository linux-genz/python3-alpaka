PKG_CONFIG=$(shell dirname ${CROSS_COMPILE})/pkg-config
NL_LIBNAME=libnl-genl-3.0

NL_LIB_FLAGS=$(shell $(PKG_CONFIG) --cflags $(NL_LIBNAME))
NL_LIBS_L=$(shell $(PKG_CONFIG) --libs-only-L $(NL_LIBNAME))
NL_LIBS_l=$(shell $(PKG_CONFIG) --libs-only-l $(NL_LIBNAME))

KDIR := /lib/modules/$(shell uname -r)/build

obj-m += genz_genl.o

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	gcc -Wall -I/usr/include/libnl3 user_send.c -o user_send -lnl-3 -lnl-genl-3
clean:
	${MAKE} -C ${KDIR} M=$(PWD) clean
	rm -f user_send
