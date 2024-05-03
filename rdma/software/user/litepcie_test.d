litepcie_test.o : litepcie_test.c \
    liblitepcie/liblitepcie.h \
    liblitepcie/litepcie_dma.h \
    /usr/local/cuda-12.4/include/cuda.h \
    ../kernel/litepcie.h \
    ../kernel/csr.h \
    ../kernel/config.h \
    ../kernel/soc.h \
    liblitepcie/litepcie_flash.h \
    liblitepcie/litepcie_helpers.h
