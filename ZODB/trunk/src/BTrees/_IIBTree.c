/* Setup template macros */

#define MASTER_ID "$Id: _IIBTree.c,v 1.4 2002/02/20 23:59:51 jeremy Exp $\n"

#define PERSISTENT

#define MOD_NAME_PREFIX "II"
#define INITMODULE init_IIBTree
#define DEFAULT_MAX_BUCKET_SIZE 120
#define DEFAULT_MAX_BTREE_SIZE 500
                
#include "intkeymacros.h"
#include "intvaluemacros.h"
#ifndef EXCLUDE_INTSET_SUPPORT
#include "BTree/intSet.h"
#endif
#include "BTreeModuleTemplate.c"
