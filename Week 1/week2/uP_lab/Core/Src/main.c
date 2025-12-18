#include "stm32f4xx_hal.h"
#include "stm32f4xx.h"

// Lookup codes for seven-seg (common anode)
#define SEG_0		0b00111111
#define SEG_1		0b00000110
#define SEG_2		0b01011011
#define SEG_3		0b01001111
#define SEG_4		0b01100110
#define SEG_5 		0x6D //0b01101101
#define SEG_6		0b01111101
#define SEG_7		0b00000111
#define SEG_8		0b01111111
#define SEG_9		0b01100111

uint8_t cnt1 = 0;
uint8_t cnt2 = 0;

// Function Prototypes
void SystemClock_Config(void);

void GPIO_Init(void) { //pg 186 reference manual

// Enable GPIOA, GPIOB, GPIOC clock
	RCC->AHB1ENR |= 0x07;

	// PA0–PA2 input
	GPIOA->MODER &= ~0x0000003F;

	// PA0–PA2 pulldown
	GPIOA->PUPDR &= ~0x0000003F;
	GPIOA->PUPDR |=  0x0000020A;

	// PB0–PB7 output
	GPIOB->MODER &= ~0x0000FFFF;
	GPIOB->MODER |=  0x00005555;

	// PC0–PC7 output
	GPIOC->MODER &= ~0x0000FFFF;
	GPIOC->MODER |=  0x00005555;

}

static void EXTI_Init(void)
{
    // Enable SYSCFG clock (needed for EXTICR mapping)
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    // Map EXTI0 -> PA0, EXTI1 -> PA1  (EXTICR[0])
    SYSCFG->EXTICR[0] &= ~(SYSCFG_EXTICR1_EXTI0 | SYSCFG_EXTICR1_EXTI1);

    // Map EXTI4 -> PA4 (EXTICR[1], EXTICR2 macro group)
    SYSCFG->EXTICR[1] &= ~(SYSCFG_EXTICR2_EXTI4);

    // Unmask EXTI0/1/4
    EXTI->IMR |= (EXTI_IMR_IM0 | EXTI_IMR_IM1 | EXTI_IMR_IM4);

    // Rising edge enable, falling edge disable
    EXTI->RTSR |= (EXTI_RTSR_TR0 | EXTI_RTSR_TR1 | EXTI_RTSR_TR4);
    EXTI->FTSR &= ~(EXTI_FTSR_TR0 | EXTI_FTSR_TR1 | EXTI_FTSR_TR4);

    // Clear any pending flags (write 1 to clear)
    EXTI->PR = (EXTI_PR_PR0 | EXTI_PR_PR1 | EXTI_PR_PR4);

    // Enable NVIC IRQs
    NVIC_SetPriority(EXTI0_IRQn, 2);
    NVIC_EnableIRQ(EXTI0_IRQn);

    NVIC_SetPriority(EXTI1_IRQn, 2);
    NVIC_EnableIRQ(EXTI1_IRQn);

    NVIC_SetPriority(EXTI4_IRQn, 2);
    NVIC_EnableIRQ(EXTI4_IRQn);
}


int main(void) {
	HAL_Init();
	GPIO_Init();
    EXTI_Init();

	while (1) {
		switch (cnt1) {
		case 0:
			GPIOB->ODR = SEG_0;
			break;
		case 1:
			GPIOB->ODR = SEG_1;
			break;
		case 2:
			GPIOB->ODR = SEG_2;
			break;
		case 3:
			GPIOB->ODR = SEG_3;
			break;
		case 4:
			GPIOB->ODR = SEG_4;
			break;
		case 5:
			GPIOB->ODR = SEG_5;
			break;
		case 6:
			GPIOB->ODR = SEG_6;
			break;
		case 7:
			GPIOB->ODR = SEG_7;
			break;
		case 8:
			GPIOB->ODR = SEG_8;
			break;
		case 9:
			GPIOB->ODR = SEG_9;
			break;
		}

		switch (cnt2) {
		case 0:
			GPIOC->ODR = SEG_0;
			break;
		case 1:
			GPIOC->ODR = SEG_1;
			break;
		case 2:
			GPIOC->ODR = SEG_2;
			break;
		case 3:
			GPIOC->ODR = SEG_3;
			break;
		case 4:
			GPIOC->ODR = SEG_4;
			break;
		case 5:
			GPIOC->ODR = SEG_5;
			break;
		case 6:
			GPIOC->ODR = SEG_6;
			break;
		case 7:
			GPIOC->ODR = SEG_7;
			break;
		case 8:
			GPIOC->ODR = SEG_8;
			break;
		case 9:
			GPIOC->ODR = SEG_9;
			break;
		}
	}
}

uint8_t flag;


void EXTI0_IRQHandler(void)
{

	if(EXTI->PR & (1<< 0))
	{
		EXTI->PR |= (1<< 0);
		if(cnt1<9) cnt1++;

	}

}

void EXTI1_IRQHandler(void)
{

	if(EXTI->PR & (1<< 1))
	{
		EXTI->PR |= (1<< 1);
		if(cnt2<9)cnt2++;
	}
}

void EXTI4_IRQHandler(void)
{

	if(EXTI->PR & (1<< 4))
	{
		EXTI->PR |= (1<<4);
		cnt1 = 0;
		cnt2 = 0;
	}
}

