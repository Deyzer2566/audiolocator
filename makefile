.PHONY: flash
CMSIS_PATH=CMSIS_6
CMSIS_STM32_PATH=cmsis-device-f1
SOURCES = \
	main.c \
	$(CMSIS_STM32_PATH)/Source/Templates/gcc/startup_stm32f103xb.s \
	$(CMSIS_STM32_PATH)/Source/Templates/system_stm32f1xx.c
#	lol.c
# syscalls.c
INCLUDES = \
	$(CMSIS_PATH)/CMSIS/Core/Include \
	$(CMSIS_STM32_PATH)/Include
DEFINES = \
	STM32F103xB
CPPFLAGS = \
	$(addprefix -I,$(INCLUDES)) \
	$(addprefix -D,$(DEFINES))
CFLAGS = \
	-mcpu=cortex-m3 \
	-msoft-float \
	-Wall \
	-g
LD_PATH = \
	STM32F103X8_FLASH.ld
LDFLAGS = \
	-T$(LD_PATH) \
	-lnosys \
	-lc \
	-lgcc \
	-specs=nano.specs \
	-specs=nosys.specs.
OUT=out
OBJECTS = $(SOURCES:.c=.o)
OBJECTS := $(OBJECTS:.s=.o)
OBJECTS := $(addprefix $(OUT)/, $(OBJECTS))
all: flash
flash: $(OUT)/audiolocator.bin
	st-flash write $(OUT)/audiolocator.bin 0x8000000
$(OUT)/audiolocator.bin: $(OUT)/audiolocator.elf
	@arm-none-eabi-objcopy -O binary $(OUT)/audiolocator.elf $(OUT)/audiolocator.bin
$(OUT)/audiolocator.elf: $(OBJECTS)
	@arm-none-eabi-gcc $^ $(LDFLAGS) -o $@ $(CFLAGS)
$(OUT)/%.o: %.c
	@$(shell mkdir --parents "$(dir $@)")
	@arm-none-eabi-gcc -c $^ -o $@ $(CPPFLAGS) $(CFLAGS)
$(OUT)/%.o: %.s
	@$(shell mkdir --parents "$(dir $@)")
	@arm-none-eabi-gcc -c $^ -o $@ $(CFLAGS)