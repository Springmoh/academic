/*----------------------------------------------------------------------------
 * Name:    Exti.c
 * Purpose: EXTI usage for STM32
 * Version: V1.00
 *----------------------------------------------------------------------------
 * This file is part of the uVision/ARM development tools.
 * This software may only be used under the terms of a valid, current,
 * end user licence from KEIL for a compatible version of KEIL software
 * development tools. Nothing else gives you the right to use this software.
 *
 * Copyright (c) 2005-2007 Keil Software. All rights reserved.
 *----------------------------------------------------------------------------*/

#include <stm32f10x_lib.h>                        // STM32F10x Library Definitions
#include "STM32_Init.h"                           // STM32 Initialization


unsigned int ledPosExti = 0;                      // led position (from 0..7) for EXTI
unsigned int ledExti    = 0;


/*----------------------------------------------------------------------------
  EXTI0 Interrupt Handler      for WKUP button connected to GPIOA.0
 *----------------------------------------------------------------------------*/
void EXTI0_IRQHandler(void)
{
  if (EXTI->PR & (1<<0)) {                        // EXTI13 interrupt pending?
    EXTI->PR |= (1<<0);                           // clear pending interrupt

    if ((ledExti ^=1) == 0) 
      GPIOB->ODR &= ~(1 << (ledPosExti+8));       // switch off LED
    else
      GPIOB->ODR |=  (1 << (ledPosExti+8));       // switch on  LED
  }
}


/*----------------------------------------------------------------------------
  EXTI15..10 Interrupt Handler for TAMP button connected to GPIOC.13
 *----------------------------------------------------------------------------*/
void EXTI15_10_IRQHandler(void)
{
  if (EXTI->PR & (1<<13)) {                       // EXTI0 interrupt pending?
    EXTI->PR |= (1<<13);                          // clear pending interrupt

    if ((ledExti ^=1) == 0) 
      GPIOB->ODR &= ~(1 << (ledPosExti+8));       // switch off LED
    else
      GPIOB->ODR |=  (1 << (ledPosExti+8));       // switch on  LED
  }
}


/*----------------------------------------------------------------------------
  MAIN function
 *----------------------------------------------------------------------------*/
int main (void) {

  stm32_Init ();                                  // STM32 setup
    
  while (1) {                                     // Loop forever
    ;
  } // end while
} // end main
