//
//  tcs.c
//  kstat-firmware
//
//  Created by Michael Dryden on 2015-09-25.
//  Copyright © 2015 wheeler lab. All rights reserved.
//

#include "tcs.h"
#include <twi_master.h>
#include <twi_common.h>
#include <ioport.h>
#include <sysclk.h>
#include "kstat_config.h"

#define TCS_TWI EXT_TWI0

#define SLAVE_ADDR 0x29
#define TCS_EN 0x00
#define TCS_TIMING 0x01
#define TCS_DATA 0x14
#define TCS_INTERRUPT 0b10000010
#define TCS_CTRL 0x0F

void tcs_init(void){
    twi_package_t twi_pack;
    
    uint8_t data_buffer = 0b00000011;
    
    twi_pack.addr[0] = TCS_EN;
    twi_pack.addr_length = 1;
    twi_pack.buffer = &data_buffer;
    twi_pack.chip = SLAVE_ADDR;
    twi_pack.length = 1;
    twi_pack.no_wait = false;
    twi_master_write(&TCS_TWI, &twi_pack);
    
    data_buffer = 0xC0;
    twi_pack.addr[0] = 1 << 7 | TCS_TIMING;
    twi_master_write(&TWIC, &twi_pack);
    
    data_buffer = 0b00000011; //prescale
    twi_pack.addr[0] = 1 << 7 | TCS_CTRL;
    twi_master_write(&TWIC, &twi_pack);
    
    return;
}

void tcs_readvalues(uint16_t data[4]){
    union data_buffer_t{
        uint16_t uint16[4];
        uint8_t uint8[4][2];
    }data_buffer;
    twi_package_t twi_pack;
    
    twi_pack.addr[0] = 0b10100000|TCS_DATA;
    twi_pack.addr_length = 1;
    twi_pack.buffer = &(data_buffer.uint8[0][0]);
    twi_pack.chip = SLAVE_ADDR;
    twi_pack.no_wait = false;
    
    twi_pack.length = 8;
    twi_master_read(&TWIC, &twi_pack);
    
    data[0] = data_buffer.uint16[0];
    data[1] = data_buffer.uint16[1];
    data[2] = data_buffer.uint16[2];
    data[3] = data_buffer.uint16[3];
    
    return;
}
