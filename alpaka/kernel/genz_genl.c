#include <linux/module.h>
#include <linux/netlink.h>
#include <net/genetlink.h>

#include "genz_genl.h"

MODULE_DESCRIPTION("Demo Generic Netlink Receiver for Linux Gen-Z subsystem");
MODULE_AUTHOR("Betty Dall, Zach Volchak, Rocky Craig @hpe.com");
MODULE_VERSION("0.98");
MODULE_LICENSE("GPL");

/* Generic Netlink Attribute Policy */
static struct nla_policy genz_nla_policy[] = {
    [GENZ_A_GCID] = { .type = NLA_U32 },
    [GENZ_A_CCLASS] = { .type = NLA_U16 },
    [GENZ_A_UUID] = { .len = UUID_LEN }
};

/* Netlink Generic Handler: parse command and attributes and choose (in)action.
   Return 0 on success else -ESOMETHING */

static int genz_genl_dispatch(struct sk_buff *skb, struct genl_info *info)
{
	struct nlattr *tmp;
	int errors = 0;
	uint32_t GCID = 0, cmd;
	uint16_t CCLASS = 0;
	uint8_t *UUID = NULL;	// must be kfree'd

	cmd = info->genlhdr->cmd;
	pr_info("%s: cmd=%u portid=%u (0x%x) seq=%u\n", __FUNCTION__,
		cmd,
		info->snd_portid,
		info->snd_portid,
		info->snd_seq);

	if (!(tmp = info->attrs[GENZ_A_GCID])) {
		pr_err("\tmissing GCID\n");
		errors++;
	} else {
		GCID = nla_get_u32(tmp);
		pr_info("\tGCID = %u\n", GCID);
	}

	if (!(tmp = info->attrs[GENZ_A_CCLASS])) {
		pr_err("\tmissing CCLASS\n");
		errors++;
	} else {
		CCLASS = nla_get_u16(tmp);
		pr_info("\tCCLASS = %u\n", CCLASS);
	}

	if (!(tmp = info->attrs[GENZ_A_UUID])) {
		pr_err("\tmissing UUID\n");
		errors++;
	} else {
		unsigned i;

		UUID = nla_memdup(tmp, GFP_KERNEL);
		pr_info("\tUUID = ");
		for (i = 0; i < UUID_LEN; i++)
			pr_cont("%02x", *(UUID + i));
		if (tmp->nla_len != UUID_LEN)
			pr_warn("\tUUID NLA length = %d, not 16\n",
				tmp->nla_len);
	}

	switch(cmd) {
	case GENZ_C_ADD_COMPONENT:
		pr_info("\tDispatch: ADD_COMPONENT\n");
		break;
	case GENZ_C_REMOVE_COMPONENT:
		pr_info("\tDispatch: REMOVE_COMPONENT\n");
		break;
	case GENZ_C_SYMLINK_COMPONENT:
		pr_info("\tDispatch: SYMLINK_COMPONENT\n");
		break;
	default:
		pr_err("\tBad command %u (TSNH :-)\n", cmd);
		errors++;
		break;
	}

	if (UUID)
		kfree(UUID);
	pr_info("Exiting %s, errors=%d\n", __FUNCTION__, errors);
	return errors ? -EMEDIUMTYPE : 0;
}

/* Netlink Generic Operations, registered to the kernel to direct requests. */
static struct genl_ops genz_genl_ops[] = {
    {
    .cmd = GENZ_C_ADD_COMPONENT,
    .doit = genz_genl_dispatch,		// Simple demo, common handler
    .policy = genz_nla_policy,		// Simple demo, common attributes
    },
    {
    .cmd = GENZ_C_REMOVE_COMPONENT,
    .doit = genz_genl_dispatch,
    .policy = genz_nla_policy,
    },
    {
    .cmd = GENZ_C_SYMLINK_COMPONENT,
    .doit = genz_genl_dispatch,
    .policy = genz_nla_policy,
    },
};//genz_genl_ops

/* Netlink Generic Family Definition */
static struct genl_family genz_genl_family = {
    .name = GENZ_GENL_FAMILY_NAME,
    .version = GENZ_GENL_VERSION,
    .hdrsize = GENZ_GENL_USER_HEADER_SIZE,
    .maxattr = ARRAY_SIZE_AS_GOD_INTENDED(genz_nla_policy),
    .ops = genz_genl_ops,
    .n_ops = ARRAY_SIZE_AS_GOD_INTENDED(genz_genl_ops)
};//genz_genl_family

static int __init genz_genl_init(void) {
    int ret;

    pr_info("Entering %s()\n", __FUNCTION__);
    ret = genl_register_family(&genz_genl_family);
    if (ret != 0) {
        pr_err("genl_register_family() returned %d\n", ret);
        return -1;
    }
    return 0;
}//nl_init


static void __exit genz_genl_exit(void) {
    pr_info("Entering %s()\n", __FUNCTION__);
    genl_unregister_family(&genz_genl_family);
}//nl_exit

module_init(genz_genl_init);
module_exit(genz_genl_exit);
