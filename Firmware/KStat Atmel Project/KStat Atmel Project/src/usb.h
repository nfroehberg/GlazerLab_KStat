//
//  usb.h
//  kstat-firmware
//
//  Created by Michael Dryden on 2017-05-04.
//  Copyright © 2017 Michael Dryden. All rights reserved.
//

#ifndef usb_h
#define usb_h

#include <stdio.h>
#include "config/conf_usb.h"

void my_callback_cdc_set_rts(uint8_t port, uint8_t b_enable);
uint8_t serial_number[USB_DEVICE_GET_SERIAL_NAME_LENGTH];
void init_build_usb_serial_number(void);

#endif /* usb_h */
