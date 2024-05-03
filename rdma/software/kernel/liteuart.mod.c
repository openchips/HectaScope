#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/export-internal.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

#ifdef CONFIG_UNWINDER_ORC
#include <asm/orc_header.h>
ORC_HEADER;
#endif

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif



static const char ____versions[]
__used __section("__versions") =
	"\x18\x00\x00\x00\xa2\x3e\x99\xc9"
	"handle_sysrq\0\0\0\0"
	"\x18\x00\x00\x00\x55\x48\x0e\xdc"
	"timer_delete\0\0\0\0"
	"\x1c\x00\x00\x00\x43\xd6\xa7\x1f"
	"uart_write_wakeup\0\0\0"
	"\x24\x00\x00\x00\x7f\x75\xc4\x63"
	"platform_driver_unregister\0\0"
	"\x18\x00\x00\x00\x10\x6d\x86\xba"
	"devm_kmalloc\0\0\0\0"
	"\x20\x00\x00\x00\x5d\x7b\xc1\xe2"
	"__SCT__might_resched\0\0\0\0"
	"\x18\x00\x00\x00\x64\xbd\x8f\xba"
	"_raw_spin_lock\0\0"
	"\x14\x00\x00\x00\x16\xb6\x14\x91"
	"__xa_alloc\0\0"
	"\x1c\x00\x00\x00\x34\x4b\xb5\xb5"
	"_raw_spin_unlock\0\0\0\0"
	"\x1c\x00\x00\x00\x0c\xc2\xe5\xf5"
	"uart_add_one_port\0\0\0"
	"\x1c\x00\x00\x00\xcb\xf6\xfd\xf0"
	"__stack_chk_fail\0\0\0\0"
	"\x18\x00\x00\x00\x39\x63\xf4\xc6"
	"init_timer_key\0\0"
	"\x14\x00\x00\x00\xbb\x6d\xfb\xbd"
	"__fentry__\0\0"
	"\x1c\x00\x00\x00\xca\x39\x82\x5b"
	"__x86_return_thunk\0\0"
	"\x20\x00\x00\x00\x1b\x9e\xd1\xc4"
	"uart_register_driver\0\0\0\0"
	"\x24\x00\x00\x00\x5e\x95\x41\x76"
	"__platform_driver_register\0\0"
	"\x20\x00\x00\x00\x7a\xd6\xa7\x6b"
	"uart_unregister_driver\0\0"
	"\x20\x00\x00\x00\x34\xd0\xe2\x1d"
	"uart_remove_one_port\0\0\0\0"
	"\x14\x00\x00\x00\x81\xa9\x45\x07"
	"xa_erase\0\0\0\0"
	"\x20\x00\x00\x00\x0b\x05\xdb\x34"
	"_raw_spin_lock_irqsave\0\0"
	"\x1c\x00\x00\x00\x02\xee\xf8\x23"
	"uart_get_baud_rate\0\0"
	"\x1c\x00\x00\x00\x47\xd9\xac\x76"
	"uart_update_timeout\0"
	"\x24\x00\x00\x00\x70\xce\x5c\xd3"
	"_raw_spin_unlock_irqrestore\0"
	"\x10\x00\x00\x00\xa6\x50\xba\x15"
	"jiffies\0"
	"\x1c\x00\x00\x00\xae\x67\x2f\xea"
	"uart_insert_char\0\0\0\0"
	"\x20\x00\x00\x00\x31\x58\xdd\x1b"
	"tty_flip_buffer_push\0\0\0\0"
	"\x1c\x00\x00\x00\x8b\x8e\xae\xff"
	"nsecs_to_jiffies\0\0\0\0"
	"\x14\x00\x00\x00\xb8\x83\x8c\xc3"
	"mod_timer\0\0\0"
	"\x14\x00\x00\x00\x66\xed\x17\x4a"
	"sysrq_mask\0\0"
	"\x20\x00\x00\x00\x9d\x19\xf4\xd3"
	"uart_try_toggle_sysrq\0\0\0"
	"\x18\x00\x00\x00\x72\x3f\x86\xba"
	"module_layout\0\0\0"
	"\x00\x00\x00\x00\x00\x00\x00\x00";

MODULE_INFO(depends, "");

MODULE_ALIAS("of:N*T*Clitex,liteuart");
MODULE_ALIAS("of:N*T*Clitex,liteuartC*");

MODULE_INFO(srcversion, "4FE99C841B93A7D1F83F652");
