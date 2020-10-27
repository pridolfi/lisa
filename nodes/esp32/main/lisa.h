/*  
    LISA - Main header file
    Copyright (C) 2020 Pablo Ridolfi

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

#ifndef LISA_H
#define LISA_H

/*==================[inclusions]=============================================*/

#include <stddef.h>
#include <stdint.h>

/*==================[macros]=================================================*/

/*==================[typedef]================================================*/

/**
 * @brief command handler
 * 
 * this handler is executed when the corresponded command is received
 * 
 * user can return a response using the response parameter
 * 
 */
typedef int32_t (*command_handler_t)(int8_t * params, int8_t * response);

/** @brief lisa command structure */
typedef struct {
    const char * command;
    command_handler_t handler;
} lisa_command_t;

/*==================[external data declaration]==============================*/

/*==================[configuration data declaration]=========================*/

extern const char node_id[];
extern const unsigned char node_private_key[];
extern const unsigned char dispatcher_public_key[];
extern const char dispatcher_ip[];
extern const short dispatcher_port;
extern const lisa_command_t lisa_commands[];

/*==================[external functions declaration]=========================*/

int32_t lisa_start(void);

/*==================[end of file]============================================*/
#endif /* #ifndef LISA_H */