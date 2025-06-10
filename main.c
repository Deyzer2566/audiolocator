#include <stm32f103xb.h>
#include <stdbool.h>

#define BLOCKSIZE 800
#pragma pack(push, 1)
struct packet_t {
    uint8_t header;
    uint8_t cnt;
    uint8_t adc_data[BLOCKSIZE];
    uint32_t sum;
    uint8_t end;
};
#pragma pack(pop)
struct packet_t packet[2];
uint8_t adc_buff_num = 0;
uint16_t adc_data_counter=0;
uint16_t adc_data_send_counter=0;
uint8_t packet_num = 0;
uint32_t sum = 0;
void USART2_IRQHandler() {
    if((USART2->SR & USART_SR_TXE) && (USART2->CR1 & USART_CR1_TXEIE)) {
        USART2->DR = ((uint8_t*)&packet[(adc_buff_num+1)%2])[adc_data_send_counter];
        adc_data_send_counter++;
        if(adc_data_send_counter == sizeof(struct packet_t)) {
            USART2->CR1 &= ~USART_CR1_TXEIE;
            adc_data_send_counter=0;
        }
    }
}

void ADC1_2_IRQHandler() {
    uint16_t adc = ADC1->DR;
    packet[adc_buff_num].adc_data[adc_data_counter] = adc>>8;
    adc_data_counter++;
    packet[adc_buff_num].adc_data[adc_data_counter] = adc;
    adc_data_counter++;
    sum += ((adc>>8)&0xff) + (adc&0xff);
    if(adc_data_counter == BLOCKSIZE) {
        packet[adc_buff_num].header = 0x69;
        packet[adc_buff_num].end = 0x96;
        packet[adc_buff_num].cnt = packet_num++;
        packet[adc_buff_num].sum = sum;
        if(!(USART2->CR1 & USART_CR1_TXEIE))
            USART2->CR1 |= USART_CR1_TXEIE;
        else
            GPIOC->ODR |= GPIO_ODR_ODR13;
        adc_data_counter = 0;
        adc_buff_num = (adc_buff_num+1)%2;
        sum = 0;
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
    USART2->BRR = 8000000/200000;

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
    NVIC_SetPriority(USART2_IRQn, 1);
    NVIC_EnableIRQ(USART2_IRQn);
    while(1) {
        __NOP();
    }
}