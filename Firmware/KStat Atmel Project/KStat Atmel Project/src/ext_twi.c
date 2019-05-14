//
//  ext_twi.c
//  kstat-firmware
//
//  Created by Michael Dryden on 2017-02-19.
//  Copyright © 2017 Michael Dryden. All rights reserved.
//

#include "ext_twi.h"

#include "config/kstat_config.h"
#include <ioport.h>
#include <sysclk.h>
#include <twi_common.h>
#include <twi_master.h>

void ext_twi_init(void){
    ioport_set_pin_mode(EXT_TWI0_SDA, IOPORT_MODE_WIREDANDPULL);
    ioport_set_pin_mode(EXT_TWI0_SCL, IOPORT_MODE_WIREDANDPULL);
    sysclk_enable_peripheral_clock(&EXT_TWI0);
    twi_master_enable(&EXT_TWI0);
    
    twi_master_options_t opt = {
        .speed = EXT_TWI0_SPEED,
        .chip  = EXT_TWI0_MASTER_ADDR
    };
    
    twi_master_setup(&EXT_TWI0, &opt);
    printf("#INFO: TWI master enabled\n");
}
