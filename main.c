#include <stm32f103xb.h>
#include <stdbool.h>

#define BLOCKSIZE 800
uint8_t adc_data[2][BLOCKSIZE];
uint8_t adc_buff_num = 0;
uint16_t adc_data_counter=0;
uint16_t adc_data_send_counter=0;
#define END_CHAR 0x13
#define ESC_CHAR 0xdd
#define ESC_END 0x15
#define ESC_ESC 0xdb
bool start_send = false;
bool escaped = false;
uint8_t escaped_char;
uint8_t packet_num = 0;
uint32_t sum = 0;
void USART2_IRQHandler() {
    if((USART2->SR & USART_SR_TXE) && (USART2->CR1 & USART_CR1_TXEIE)) {
        uint8_t byte_to_send;
        if(start_send) {
            if(escaped) {
                escaped = false;
                byte_to_send = escaped_char;
            } else {
                uint8_t byte;
                if(adc_data_send_counter < BLOCKSIZE) {
                    byte = adc_data[(adc_buff_num+1)%2][adc_data_send_counter];
                    sum += byte;
                } else if(adc_data_send_counter == BLOCKSIZE){
                    byte = packet_num++;
                } else {
                    byte = (sum>>(8*(adc_data_send_counter-BLOCKSIZE-1)))&0xff;
                }
                adc_data_send_counter++;
                if(byte == END_CHAR || byte == ESC_CHAR) {
                    escaped_char = (byte==END_CHAR)?ESC_END:ESC_ESC;
                    escaped = true;
                    byte_to_send = ESC_CHAR;
                } else {
                    byte_to_send = byte;
                }
            }
        } else {
            byte_to_send = END_CHAR;
            start_send = true;
        }
        if(adc_data_send_counter == BLOCKSIZE+5 && !escaped) {
            adc_data_send_counter = 0;
            USART2->CR1 &= ~USART_CR1_TXEIE;
            start_send = false;
            sum = 0;
        }
        USART2->DR = byte_to_send;
    }
}

void ADC1_2_IRQHandler() {
    uint16_t adc = ADC1->DR;
    adc_data[adc_buff_num][adc_data_counter] = adc>>8;
    adc_data_counter++;
    adc_data[adc_buff_num][adc_data_counter] = adc;
    adc_data_counter++;
    if(adc_data_counter == BLOCKSIZE) {
        USART2->CR1 |= USART_CR1_TXEIE;
        adc_data_counter = 0;
        adc_buff_num = (adc_buff_num+1)%2;
    }
}

__attribute__((noreturn))
int main() {
    RCC->CR |= RCC_CR_HSEON;
    while(!(RCC->CR & RCC_CR_HSERDY)){}
    RCC->CFGR |= RCC_CFGR_SW_0;
    while(!(RCC->CFGR & RCC_CFGR_SWS_0)){}

    RCC->APB2ENR |= RCC_APB2ENR_IOPCEN;
    GPIOC->CRH &= ~GPIO_CRH_MODE13;
    GPIOC->CRH |= GPIO_CRH_MODE13_0;
    GPIOC->CRH &= ~GPIO_CRH_CNF13;

    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;
    GPIOA->CRL &= ~(GPIO_CRL_CNF2|GPIO_CRL_MODE2);
    GPIOA->CRL |= GPIO_CRL_CNF2_1 | GPIO_CRL_MODE2_0;

    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    USART2->CR1 |= USART_CR1_UE | USART_CR1_TE;
    USART2->BRR = 8000000/115200;

    GPIOA->CRL &= ~(GPIO_CRL_CNF0|GPIO_CRL_MODE0);

    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;
    RCC->CFGR |= RCC_CFGR_ADCPRE;
    ADC1->CR2 |= ADC_CR2_ADON;
    for(int i = 0;i<10;i++) {}
    ADC1->CR2 |= ADC_CR2_CAL;
    while(ADC1->CR2 & ADC_CR2_CAL){}
    ADC1->SMPR2 |= ADC_SMPR2_SMP0;
    ADC1->SQR1 &= ~ADC_SQR1_L;
    ADC1->SQR3 &= ~ADC_SQR3_SQ1;
    ADC1->CR1 |= ADC_CR1_EOCIE;
    ADC1->CR2 |= ADC_CR2_CONT;
    ADC1->CR2 |= ADC_CR2_ADON;
    NVIC_EnableIRQ(ADC1_2_IRQn);
    NVIC_EnableIRQ(USART2_IRQn);
    while(1) {
        GPIOC->BSRR = GPIO_BSRR_BR13;
        for(int i = 0;i<100000;i++);
        GPIOC->BSRR = GPIO_BSRR_BS13;
        for(int i = 0;i<100000;i++);
    }
}