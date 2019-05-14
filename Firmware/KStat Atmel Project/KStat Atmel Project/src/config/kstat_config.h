//
//  kstat_config.h
//  kstat-firmware
//
//  Created by Michael Dryden on 2017-02-19.
//  Copyright © 2017 Michael Dryden. All rights reserved.
//

#ifndef kstat_config_h
#define kstat_config_h

#include <ioport.h>

#define EXT_TWI0                TWIC
#define EXT_TWI0_SDA            IOPORT_CREATE_PIN(PORTC,0)
#define EXT_TWI0_SCL            IOPORT_CREATE_PIN(PORTC,1)
#define EXT_TWI0_MASTER_ADDR    0x42
#define EXT_TWI0_SPEED          100000

#endif /* kstat_config_h */
