/*  
    LISA - Main example source file
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

/*==================[inclusions]=============================================*/

#include <string.h>

#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"

#include "wifi_connect.h"
#include "lisa.h"

/*==================[macros and definitions]=================================*/

/*==================[internal data declaration]==============================*/

/*==================[internal functions declaration]=========================*/

/*==================[internal data definition]===============================*/

static const char *TAG = node_id;

/*==================[external data definition]===============================*/

/*==================[internal functions definition]==========================*/

/*==================[external functions definition]==========================*/

void app_main(void)
{
    char from[32];
    char msg[128];

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    ESP_ERROR_CHECK(wifi_connect());
    ESP_LOGI(TAG, "lisa_start: %d", lisa_start());

    while (1) {
        if (!lisa_recv_message(from, 32, msg, 128)) {
            ESP_LOGI(TAG, "message from %s: %s", from, msg);
            lisa_send_message(from, "Hi! How are you?");
        }
        vTaskDelay(10);
    }
}

/*==================[end of file]============================================*/