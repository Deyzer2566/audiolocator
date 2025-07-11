#include <stm32f103xb.h>
#include <stdbool.h>

#define CHANNEL_SIZE (200)
#define CHANNELS (2)
#define BLOCKSIZE (CHANNEL_SIZE * CHANNELS)
struct packet_t {
    uint8_t header;
    uint8_t cnt;
    uint16_t adc_data[BLOCKSIZE];
#if ((BLOCKSIZE+2) % 4 != 0)
    uint8_t align1[(BLOCKSIZE+2) % 4];
#endif
    uint32_t sum;
    uint8_t end;
};
struct packet_t packet[2];
uint8_t adc_buff_num = 0;
uint8_t packet_num = 0;
uint32_t sum = 0;
extern uint32_t SystemCoreClock;

void DMA1_Channel1_IRQHandler() {
    if(DMA1->ISR & DMA_ISR_TCIF1) {
        if(!(USART2->SR & USART_SR_TC)) {
            GPIOC->ODR |= GPIO_ODR_ODR13;
        }
        DMA1_Channel1->CCR &= ~DMA_CCR_EN;
        DMA1_Channel1->CMAR = (uint32_t)(&packet[(adc_buff_num+1)%2].adc_data[0]);
        DMA1_Channel1->CNDTR = BLOCKSIZE;
        DMA1->IFCR = DMA_IFCR_CTCIF1;
        DMA1_Channel1->CCR |= DMA_CCR_EN;
        packet[adc_buff_num].header = 0x69;
        packet[adc_buff_num].end = 0x96;
        packet[adc_buff_num].cnt = packet_num++;
        for(int i = 0;i<BLOCKSIZE;i++){
            sum += packet[adc_buff_num].adc_data[i];
        }
        packet[adc_buff_num].sum = sum;
        DMA1_Channel7->CMAR = (uint32_t)&packet[adc_buff_num];
        DMA1_Channel7->CNDTR = sizeof(struct packet_t);
        DMA1_Channel7->CCR |= DMA_CCR_EN;
        USART2->SR &= ~USART_SR_TC;
        adc_buff_num = (adc_buff_num+1)%2;
        sum = 0;
    } else if (DMA1->ISR & DMA_ISR_TEIF1) {
        GPIOC->ODR |= GPIO_ODR_ODR13;
        DMA1->IFCR = DMA_IFCR_CTEIF1;
    }
}

void DMA1_Channel7_IRQHandler() {
     if(DMA1->ISR & DMA_ISR_TCIF7) {
        DMA1_Channel7->CCR &= ~DMA_CCR_EN;
        DMA1->IFCR = DMA_IFCR_CTCIF7;
    } else  if (DMA1->ISR & DMA_ISR_TEIF7){
        GPIOC->ODR |= GPIO_ODR_ODR13;
        DMA1->IFCR = DMA_IFCR_CTEIF7;
    }
}

void switch_to_hse() {
    RCC->CR |= RCC_CR_HSEON;
    while(!(RCC->CR & RCC_CR_HSERDY)){}
    RCC->CFGR |= RCC_CFGR_SW_0;
    while(!(RCC->CFGR & RCC_CFGR_SWS_0)){}
}

void enable_pc13() {
    RCC->APB2ENR |= RCC_APB2ENR_IOPCEN;
    GPIOC->CRH &= ~GPIO_CRH_MODE13;
    GPIOC->CRH |= GPIO_CRH_MODE13_0;
    GPIOC->CRH &= ~GPIO_CRH_CNF13;
}

void init_uart() {
    RCC->APB2ENR |= RCC_APB2ENR_IOPAEN;
    GPIOA->CRL &= ~(GPIO_CRL_CNF2|GPIO_CRL_MODE2);
    GPIOA->CRL |= GPIO_CRL_CNF2_1 | GPIO_CRL_MODE2_0;

    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;
    USART2->CR1 |= USART_CR1_UE | USART_CR1_TE;
    USART2->BRR = SystemCoreClock/200000;
    USART2->CR3 |= USART_CR3_DMAT;
}

/* 
 * Таймер опроса АЦП
 * Частота дискретизации = 8.000.000 Гц/100/20 == 4 кГц
 */
void init_tim3() {
    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
    TIM3->PSC = 100-1;
    TIM3->ARR = 20-1;
    TIM3->CR2 = /*update event as timer's trigger out*/TIM_CR2_MMS_1;
    TIM3->EGR = TIM_EGR_TG | TIM_EGR_UG;
}

void start_adc() {
    DMA1_Channel1->CCR |= DMA_CCR_EN;
    TIM3->CR1 = TIM_CR1_CEN;
}

void init_adc() {
    GPIOA->CRL &= ~(GPIO_CRL_CNF0|GPIO_CRL_MODE0);
    GPIOA->CRL &= ~(GPIO_CRL_CNF1|GPIO_CRL_MODE1);
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;
    ADC1->CR2 |= ADC_CR2_ADON;
    ADC1->CR2 |= ADC_CR2_RSTCAL;
    while(ADC1->CR2 & ADC_CR2_RSTCAL) {}
    for(int i = 0;i<10;i++){}
    ADC1->CR2 |= ADC_CR2_CAL;
    while(ADC1->CR2 & ADC_CR2_CAL) {}
    ADC1->CR2 &= ~ADC_CR2_ADON;
    ADC1->CR2 |= ADC_CR2_EXTSEL_2;// TIM3 TRGO as external trigger
    ADC1->CR2 |= ADC_CR2_EXTTRIG;// set external trigger for conversion start
    ADC1->SQR1 &= ~ADC_SQR1_L;
    ADC1->SQR1 |= ADC_SQR1_L_0;
    ADC1->SQR3 &= ~ADC_SQR3_SQ1;
    ADC1->SQR3 |= ADC_SQR3_SQ2_0; // second conversion on second channel
    ADC1->CR1 |= ADC_CR1_SCAN;
    ADC1->CR2 |= ADC_CR2_DMA;
    ADC1->CR2 |= ADC_CR2_ADON;
}

void init_dma() {
    RCC->AHBENR |= RCC_AHBENR_DMA1EN;
    while(!(RCC->AHBENR & RCC_AHBENR_DMA1EN));
    DMA1_Channel1->CCR = DMA_CCR_MINC | DMA_CCR_TCIE | DMA_CCR_TEIE | DMA_CCR_MSIZE_0 | DMA_CCR_PSIZE_0 | DMA_CCR_PL_0;
    DMA1_Channel1->CNDTR = BLOCKSIZE;
    DMA1_Channel1->CPAR = (uint32_t)&ADC1->DR;
    DMA1_Channel1->CMAR = (uint32_t)(&packet[adc_buff_num].adc_data[0]);

    DMA1_Channel7->CCR = DMA_CCR_MINC | DMA_CCR_TCIE | DMA_CCR_TEIE | DMA_CCR_DIR;
    DMA1_Channel7->CPAR = (uint32_t)&USART2->DR;
}

__attribute__((noreturn))
int main() {
    SystemCoreClock = (uint32_t)8000000;
    switch_to_hse();

    enable_pc13();

    init_uart();

    init_tim3();

    init_adc();

    init_dma();
    NVIC_EnableIRQ(DMA1_Channel1_IRQn);
    NVIC_EnableIRQ(DMA1_Channel7_IRQn);
    
    start_adc();
    while(1) {
        __WFE();
    }
}