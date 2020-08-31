/*  
    Wi-Fi wrappers header file
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

#ifndef WIFI_CONNECT_H
#define WIFI_CONNECT_H

/*==================[inclusions]=============================================*/

#include <esp_err.h>

/*==================[macros]=================================================*/

/*==================[typedef]================================================*/

/*==================[external data declaration]==============================*/

/*==================[configuration data declaration]=========================*/

extern const char wifi_ssid[];
extern const char wifi_passwd[];

/*==================[external functions declaration]=========================*/

esp_err_t wifi_connect(void);
esp_err_t wifi_disconnect(void);

/*==================[end of file]============================================*/
#endif /* #ifndef WIFI_CONNECT_H */