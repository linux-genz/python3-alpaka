
#define GENZ_GENL_FAMILY_NAME 		"genz_cmd"
#define GENZ_GENL_VERSION		1
#define GENZ_GENL_USER_HEADER_SIZE	0
#define UUID_LEN			16	/* array of uint8_t */

#define ARRAY_SIZE_AS_GOD_INTENDED(arr) (sizeof(arr) / sizeof((arr)[0]))

// Observe convention to avoid zero as a base index or value.

/* Netlink Generic Message Attributes */
enum {
	GENZ_A_GCID=1,
	GENZ_A_CCLASS,
	GENZ_A_UUID,
};

/* user_send attributes to consolidate parameters received by kernel. */
struct MsgProps {
    char* gcid;
    char* cclass;
    char* uuid;
};

/* Netlink Generic Commands */
enum {
	GENZ_C_ADD_COMPONENT=1,
	GENZ_C_REMOVE_COMPONENT,
	GENZ_C_SYMLINK_COMPONENT,
};
