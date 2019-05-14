//
//  leds.c
//  kstat-firmware
//
//  Created by Michael Dryden on 2017-05-04.
//  Copyright © 2017 Michael Dryden. All rights reserved.
//

#include "usb.h"
#include "config/conf_board.h"
#include <ioport.h>
#include <util/atomic.h>
#include <string.h>

uint8_t ReadSignatureByte(uint16_t Address);
void NVM_GetGUID(uint8_t* bytearray);

void my_callback_cdc_set_rts(uint8_t port, uint8_t b_enable){
    static uint8_t connected = 0;
    
    #if BOARD_VER_MAJOR >= 1 && BOARD_VER_MINOR >= 2 && BOARD_VER_MICRO >=3
        ioport_set_pin_level(LED2, b_enable);
    #endif
    
    if (connected && !b_enable){
        ATOMIC_BLOCK(ATOMIC_RESTORESTATE){
            CCP = 0xD8;                        // Configuration change protection: allow protected IO regiser write
            RST.CTRL = RST_SWRST_bm;           // Request software reset by writing to protected IO register
        }
    }
    connected = b_enable;
}

void init_build_usb_serial_number(void)
{
    serial_number[0] = 'D';
    serial_number[1] = 'S';
    serial_number[2] = 'T';
    serial_number[3] = 'A';
    serial_number[4] = 'T';
    
    NVM_GetGUID(&serial_number[5]);
}

uint8_t ReadSignatureByte(uint16_t Address) {
    NVM_CMD = NVM_CMD_READ_CALIB_ROW_gc;
    uint8_t Result;
    __asm__ ("lpm %0, Z\n" : "=r" (Result) : "z" (Address));
    //  __asm__ ("lpm \n  mov %0, r0 \n" : "=r" (Result) : "z" (Address) : "r0");
    NVM_CMD = NVM_CMD_NO_OPERATION_gc;
    return Result;
}

void NVM_GetGUID(uint8_t* b) {
    enum {
        LOTNUM0=8,  // Lot Number Byte 0, ASCII
        LOTNUM1,    // Lot Number Byte 1, ASCII
        LOTNUM2,    // Lot Number Byte 2, ASCII
        LOTNUM3,    // Lot Number Byte 3, ASCII
        LOTNUM4,    // Lot Number Byte 4, ASCII
        LOTNUM5,    // Lot Number Byte 5, ASCII
        WAFNUM =16, // Wafer Number
        COORDX0=18, // Wafer Coordinate X Byte 0
        COORDX1,    // Wafer Coordinate X Byte 1
        COORDY0,    // Wafer Coordinate Y Byte 0
        COORDY1,    // Wafer Coordinate Y Byte 1
    };
    
    b[ 0]=ReadSignatureByte(LOTNUM0);
    b[ 1]=ReadSignatureByte(LOTNUM1);
    b[ 2]=ReadSignatureByte(LOTNUM2);
    b[ 3]=ReadSignatureByte(LOTNUM3);
    b[ 4]=ReadSignatureByte(LOTNUM4);
    b[ 5]=ReadSignatureByte(LOTNUM5);

}

