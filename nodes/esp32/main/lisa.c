/*  
    LISA - Main source file
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

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include "lwip/netdb.h"
#include "esp_log.h"

#include "mbedtls/pk.h"
#include "mbedtls/aes.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

#include "lisa.h"

/*==================[macros and definitions]=================================*/

#define LISA_AES_DATA_LEN MBEDTLS_MPI_MAX_SIZE
#define LISA_STACK_SIZE (4096)

/*==================[internal data declaration]==============================*/

/*==================[internal functions declaration]=========================*/

/*==================[internal data definition]===============================*/

static const char *TAG = "lisa";
static uint8_t aes_key[16];
static uint8_t aes_iv[16];
static int sock;
static struct sockaddr_in dest_addr;
static uint8_t cipher_buf[MBEDTLS_MPI_MAX_SIZE];
static uint8_t socket_buf[MBEDTLS_MPI_MAX_SIZE];
static uint8_t incoming_buffer[MBEDTLS_MPI_MAX_SIZE];
static uint8_t message_buffer[MBEDTLS_MPI_MAX_SIZE];

/*==================[external data definition]===============================*/

/*==================[internal functions definition]==========================*/

static int32_t lisa_connect(void)
{
    size_t out_len;
    struct sockaddr_in source_addr; // Large enough for both IPv4 or IPv6
    socklen_t socklen = sizeof(source_addr);
    struct timeval timeout;      
    timeout.tv_sec = 10;
    timeout.tv_usec = 0;

    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
    if (sock < 0) {
        ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
        return errno;
    }

    if (setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
        ESP_LOGE(TAG, "setsockopt SO_RCVTIMEO error %d", errno);
        return errno;
    }

    ESP_LOGI(TAG, "Socket created, connecting to %s:%d", dispatcher_ip, dispatcher_port);
    dest_addr.sin_addr.s_addr = inet_addr(dispatcher_ip);
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(dispatcher_port);

    mbedtls_entropy_context entropy;
    const unsigned char *personalization = (const unsigned char *)node_id;
    mbedtls_ctr_drbg_context ctr_drbg;
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    int32_t ret = mbedtls_ctr_drbg_seed( &ctr_drbg , mbedtls_entropy_func, &entropy,
                 personalization, strlen((const char *)personalization));
    ESP_LOGD(TAG, "mbedtls_ctr_drbg_seed: %d", ret);

    mbedtls_pk_context pk;
    mbedtls_pk_init(&pk);
    ret = mbedtls_pk_parse_public_key(&pk, dispatcher_public_key, strlen((const char*)dispatcher_public_key)+1);
    ESP_LOGD(TAG, "mbedtls_pk_parse_public_key: %d", ret);
    ret = mbedtls_pk_encrypt(&pk, (const unsigned char *)node_id, strlen(node_id), cipher_buf, &out_len, sizeof(cipher_buf), mbedtls_ctr_drbg_random, &ctr_drbg);
    ESP_LOGD(TAG, "mbedtls_pk_encrypt: %d output_len: %u", ret, out_len);
    mbedtls_pk_free(&pk);

    ret = sendto(sock, cipher_buf, out_len, 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    ESP_LOGD(TAG, "sendto NODE_ID: %d", ret);

    int len = recvfrom(sock, socket_buf, sizeof(socket_buf)-1, 0, (struct sockaddr *)&source_addr, &socklen);
    ESP_LOGD(TAG, "recvfrom aes_key: %d", len);

    if (len != 256) {
        mbedtls_entropy_free(&entropy);
        mbedtls_ctr_drbg_free(&ctr_drbg);
        ESP_LOGE(TAG, "lisa_connect error (len=%d), shutting down socket", len);
        shutdown(sock, 0);
        close(sock);
        return -1;
    }

    mbedtls_pk_init(&pk);
    ret = mbedtls_pk_parse_key(&pk, node_private_key, strlen((const char*)node_private_key)+1, NULL, 0);
    ESP_LOGD(TAG, "mbedtls_pk_parse_key: %d", ret);
    mbedtls_pk_decrypt(&pk, socket_buf, len, cipher_buf, &out_len, sizeof(cipher_buf), mbedtls_ctr_drbg_random, &ctr_drbg);
    ESP_LOGD(TAG, "mbedtls_pk_decrypt: %d output_len: %u", ret, out_len);
    mbedtls_pk_free(&pk);

    mbedtls_entropy_free(&entropy);
    mbedtls_ctr_drbg_free(&ctr_drbg);

    if ((ret == 0) && (out_len == 32)) {
        ESP_LOGI(TAG, "Connected. Setting aes key and iv.");
        memcpy(aes_key, cipher_buf, 16);
        memcpy(aes_iv, cipher_buf+16, 16);
        return 0;
    }
    ESP_LOGE(TAG, "Invalid session. Shutting down socket");
    shutdown(sock, 0);
    close(sock);
    return -1;
}

static int32_t lisa_send(void * data, size_t len)
{
    if ((data == NULL) || (len > LISA_AES_DATA_LEN)) {
        ESP_LOGE(TAG, "lisa_send: invalid data to send!");
        return -1;
    }
    uint8_t * pdata = (uint8_t *)data;
    bzero(&cipher_buf, sizeof(cipher_buf));
    bzero(&socket_buf, sizeof(socket_buf));
    memcpy(cipher_buf, pdata, len);
    size_t padding_len = 16 - (len & 0xF);
    memset(cipher_buf+len, padding_len, padding_len);
    uint8_t iv[16];
    memcpy(iv, aes_iv, 16);
    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    int ret = mbedtls_aes_setkey_enc(&aes, aes_key, 128);
    ESP_LOGD(TAG, "mbedtls_aes_setkey_enc: %d", ret);
    ret = mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_ENCRYPT, len+padding_len, iv, (uint8_t *)&cipher_buf, socket_buf);
    ESP_LOGD(TAG, "mbedtls_aes_crypt_cbc: %u %d", len+padding_len, ret);
    ret = sendto(sock, socket_buf, len+padding_len, 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    mbedtls_aes_free(&aes);
    return ret;
}

static int32_t lisa_recv(void * data, size_t len)
{
    if ((data == NULL) || (len == 0)) {
        ESP_LOGE(TAG, "lisa_send: invalid buffer parameters");
        return -1;
    }
    struct sockaddr_in source_addr; // Large enough for both IPv4 or IPv6
    socklen_t socklen = sizeof(source_addr);
    int recv_len = recvfrom(sock, socket_buf, sizeof(socket_buf)-1, 0, (struct sockaddr *)&source_addr, &socklen);
    if ((recv_len <= 0) || (recv_len & 0xF)) {
        ESP_LOGE(TAG, "lisa_recv: invalid packet size %d", recv_len);
        return -1;
    }
    uint8_t iv[16];
    memcpy(iv, aes_iv, 16);
    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    int ret = mbedtls_aes_setkey_dec(&aes, aes_key, 128);
    ESP_LOGD(TAG, "mbedtls_aes_setkey_dec: %d", ret);
    bzero(&cipher_buf, sizeof(cipher_buf));
    ret = mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_DECRYPT, recv_len, iv, socket_buf, (uint8_t *)&cipher_buf);
    mbedtls_aes_free(&aes);
    ESP_LOGD(TAG, "mbedtls_aes_crypt_cbc: %u %d", recv_len, ret);
    if (ret == 0) {
        size_t padding_len = cipher_buf[recv_len-1];
        recv_len -= padding_len;
        cipher_buf[recv_len] = 0;
        ESP_LOGD(TAG, "lisa_recv: %s", cipher_buf);
        memcpy((uint8_t*)data, cipher_buf, recv_len > len ? len : recv_len);
        return recv_len > len ? len : recv_len;
    } else {
        return -1;
    }
}

static int32_t lisa_close(void)
{
    lisa_send("close", 5);
    ESP_LOGI(TAG, "lisa_close: Shutting down socket");
    shutdown(sock, 0);
    close(sock);
    return 0;
}

static void lisa_task_thread(void * a)
{
    int rv;
    TickType_t previous_wake;

    while(1) {
        rv = lisa_connect();
        previous_wake = xTaskGetTickCount();
        while (rv >= 0) {
            if (!message_buffer[0]) {
                snprintf((char *)message_buffer, sizeof(message_buffer), "uptime:%u", esp_log_timestamp());
            }
            rv = lisa_send(message_buffer, strlen((char *)message_buffer));
            bzero(message_buffer, sizeof(message_buffer));
            rv = lisa_recv(message_buffer, sizeof(message_buffer));
            if (rv > 0) {
                ESP_LOGD(TAG, "lisa_recv: %d %s", rv, message_buffer);
                if (!memcmp(message_buffer, "msg:", 4)) {
                    strncpy((char *)incoming_buffer, (char *)message_buffer+4, strlen((char *)message_buffer)-4);
                }
            }
            bzero(message_buffer, sizeof(message_buffer));
            vTaskDelayUntil(&previous_wake, 100);
        }
        lisa_close();
        vTaskDelay(100);
    }
}

/*==================[external functions definition]==========================*/

int32_t lisa_send_message(char * receiver, char * message)
{
    if (!message_buffer[0]) {
        snprintf((char *)message_buffer, sizeof(message_buffer), "msg:%s:%s", receiver, message); 
        return 0;
    }
    return -1;
}

int32_t lisa_recv_message(char * sender, size_t sender_size, char * message, size_t message_size)
{
    if (incoming_buffer[0]) {
        strncpy(sender, strtok((char *)incoming_buffer, ":"), sender_size);
        strncpy(message, strtok(NULL, ":"), message_size);
        bzero(incoming_buffer, sizeof(incoming_buffer));
        return 0;
    }
    return -1;
}

int32_t lisa_start(void)
{
    return xTaskCreate(lisa_task_thread, "lisa_task", LISA_STACK_SIZE, NULL, tskIDLE_PRIORITY+5, NULL);
}

/*==================[end of file]============================================*/