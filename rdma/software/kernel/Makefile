# Makefile for kernel module
KERNEL_VERSION:=$(shell uname -r)
KERNEL_PATH?=/lib/modules/$(KERNEL_VERSION)/build
ARCH?=$(shell uname -m)

# Export `REPO_DIR` so that when the kernel's byzantine makefile system re-includes us,
# it's already set properly and doesn't get re-set with the wrong path.
REPO_DIR ?= $(shell dirname $(shell dirname $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))))
export REPO_DIR

NVIDIA_PATH ?= ~/open-gpu-kernel-modules/

NV_DMA ?= true

obj-m = litepcie.o liteuart.o
litepcie-objs = main.o
#liteuart-objs = liteuart.o

#ifeq ($(NV_DMA),true)
ccflags += -I$(NVIDIA_PATH)/kernel-open/nvidia -DNV_DMA=$(NV_DMA)

# don't warn about missing NVIDIA symbols; they'll be available
# TODO: create our own Module.symvers,
#       https://github.com/NVIDIA/gds-nvidia-fs/blob/af3f7de96b4e500abf30e3034e5827749953bd68/src/Makefile#L108-L112
#KBUILD_MODPOST_WARN=1


KVER ?= $(shell uname -r)
# Try to get it based on available nvidia module version (just in case there are sources for couple of versions)
nv_version=$(shell /sbin/modinfo -F version -k $(KVER) nvidia 2>/dev/null)
nv_sources=$(shell /bin/ls -d /usr/src/nvidia-$(nv_version)/ 2>/dev/null)
ifneq ($(shell test -d "$(nv_sources)" && echo "true" || echo "" ),)
	NVIDIA_SRC_DIR ?= $(shell find "$(nv_sources)" -name "nv-p2p.h"|head -1|xargs dirname || echo "NVIDIA_DRIVER_MISSING")
else
	NVIDIA_SRC_DIR ?= $(shell find /usr/src/nvidia-* -name "nv-p2p.h"|head -1|xargs dirname || echo "NVIDIA_DRIVER_MISSING")
endif
KBUILD_MODPOST_WARN=1

ccflags-y += -Wall
ccflags-y += -I$(NVIDIA_SRC_DIR)

#endif

all: litepcie.ko liteuart.ko

litepcie.ko liteuart.ko &: main.c liteuart.c litepcie.h config.h flags.h csr.h soc.h
	$(MAKE) -C $(KERNEL_PATH) ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) M=$(shell pwd) modules

modules: litepcie.ko liteuart.ko

modules_install: modules
	$(MAKE) -C $(KERNEL_PATH) ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) M=$(shell pwd) modules_install

clean:
	$(MAKE) -C $(KERNEL_PATH) ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) M=$(shell pwd) clean
	rm -f *~

print-%  : ; @echo $* = $($*)
