//
//  tcs.h
//  kstat-firmware
//
//  Created by Michael Dryden on 2015-09-25.
//  Copyright © 2015 wheeler lab. All rights reserved.
//

#ifndef tcs_h
#define tcs_h

#include <stdio.h>

void tcs_init(void);
void tcs_readvalues(uint16_t data[4]);


#endif /* tcs_h */
