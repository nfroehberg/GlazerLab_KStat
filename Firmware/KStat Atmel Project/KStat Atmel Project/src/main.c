/*
 * main.c
 *
 * Created: 29/09/2012 2:13:52 AM
 *  Author: mdryden
 */ 

#include "experiment.h"
#include "asf.h"
#include "settings.h"
#include "tcs.h"
#include "shutter.h"
#include <string.h>
#include <math.h>
#include <stdint.h>
#include "conf_board.h"
#include "ext_twi.h"
#include "usb.h"
#include <util/atomic.h>

//Internal function declarations
static void command_handler(uint16_t bytes);

static void command_handler(uint16_t bytes){
	/**
	 * Deals with commands over USB
	 *
	 * Calls functions in 
	 * @param command Command character input.
     * @param bytes Number of command bytes to wait for
	 */
    
    if (bytes == 0) {
        printf("@RCV 0\n");
        return;
    }
    else if (bytes >= MAX_COMMAND_BYTES){
        printf("@ERR Command too long\n");
        return;
    }
    
    char command_buffer[MAX_COMMAND_BYTES];
    
read_data:
    while (!udi_cdc_is_rx_ready());
    delay_ms(100);
    if(!fgets(command_buffer, MAX_COMMAND_BYTES, stdin)){
        printf("@ERR Could not read string\n");
        return;
    }
    
    command_buffer[strcspn(command_buffer, "\r\n")] = 0;
    
    if (strlen(command_buffer) == 0)
        goto read_data;
    
    printf("@RCV %u\n", strlen(command_buffer));
    printf("#%s\n", command_buffer);
    
    char command = command_buffer[0];
    
	switch (command){
        case 'E': //Experiment options
            experiment_handler(command_buffer+1);
            break;
        
        case 'S': //Settings options
            settings_handler(command_buffer+1);
            break;
            
        case 'T': ;
            uint16_t tcs_data[] = {0,0,0,0};
            if (settings.settings.tcs_enabled == 0){
                printf("T-1.-1.-1.-1\n");
            }
            else{
                tcs_readvalues(tcs_data);
                printf("#INFO: TCS—%u %u %u %u\n", tcs_data[0], tcs_data[1], tcs_data[2], tcs_data[3]);
                printf("T%u.%u.%u.%u\n", tcs_data[0], tcs_data[1], tcs_data[2], tcs_data[3]);
            }
            break;
        
        case 'R': //Restart USB
            udc_detach();
            delay_ms(100);
            udc_attach();
            break;
            
		case 'V': //check version
            #define STRING2(x) #x
            #define STRING(x) STRING2(x)
            printf("V%u.%u.%u-%lu\n", BOARD_VER_MAJOR, BOARD_VER_MINOR, BOARD_VER_MICRO);
			break;
		
		default:
			printf("@ERR Command %c not recognized\n", command);
			return;
	}
	printf("@DONE\n");
	return;
}

int main(void){
    irq_initialize_vectors();
    cpu_irq_enable();
    
	board_init();
    #if BOARD_VER_MAJOR >= 1 && BOARD_VER_MINOR >= 2 && BOARD_VER_MICRO >=3
        ioport_set_pin_dir(LED1, IOPORT_DIR_OUTPUT);
        ioport_set_pin_dir(LED2, IOPORT_DIR_OUTPUT);
    #endif
	pot_init();
	pmic_init();
	
	sysclk_init(); //Disables ALL peripheral clocks D:

	rtc_init();
    sleepmgr_init();
	sysclk_enable_module(SYSCLK_PORT_GEN, SYSCLK_EVSYS);
	
	pmic_set_scheduling(PMIC_SCH_ROUND_ROBIN);
    
    init_build_usb_serial_number();
    
	stdio_usb_init();
	
	ads1255_init_pins();
	ads1255_init_module();

	PORTD.INT0MASK = PIN5_bm;
	PORTD.INT1MASK = PIN5_bm;
	PORTD.INTCTRL = PORT_INT0LVL_OFF_gc | PORT_INT1LVL_OFF_gc;
	
	max5443_init_pins();
	max5443_init_module();
	
	ads1255_wakeup();
	ads1255_rdatac();
	ads1255_standby();
    
    ads1255_setup(ADS_BUFF_ON,ADS_DR_60,ADS_PGA_2);
    
    autogain_enable = 0;
    g_gain = POT_GAIN_30k;
    pot_set_gain();
    
    settings_read_eeprom();

    ext_twi_init();
    
    tcs_init();
    shutter_init();
	
    delay_s(1);
    udc_detach();
    delay_ms(100);
    udc_attach();
    stdio_usb_enable();
    
    uint16_t bytes_sent = 0;
    
	program_loop:
        #if BOARD_VER_MAJOR >= 1 && BOARD_VER_MINOR >= 2 && BOARD_VER_MICRO >=3
            ioport_set_pin_level(LED1, 1);
        #endif
		while (getchar() != '!');
        scanf("%u", &bytes_sent);
    
    
//        // Empty buffer
//        while (udi_cdc_is_rx_ready())
//            udi_cdc_getc();
    
		printf ("@ACK %u\n", bytes_sent);
        #if BOARD_VER_MAJOR >= 1 && BOARD_VER_MINOR >= 2 && BOARD_VER_MICRO >=3
            ioport_set_pin_level(LED1, 0);
        #endif
    
		command_handler(bytes_sent);
	goto program_loop;
}
