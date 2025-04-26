#include <stm32f103xb.h>
__attribute__((noreturn))
int main() {
    RCC->APB2ENR |= RCC_APB2ENR_IOPCEN;
    GPIOC->CRH &= ~GPIO_CRH_MODE13;
    GPIOC->CRH |= GPIO_CRH_MODE13_0;
    GPIOC->CRH &= ~GPIO_CRH_CNF13;
    while(1) {
        GPIOC->BSRR = GPIO_BSRR_BR13;
        for(int i = 0;i<10000;i++);
        GPIOC->BSRR = GPIO_BSRR_BS13;
        for(int i = 0;i<10000;i++);
    }
}