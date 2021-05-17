import pygame


if __name__ == "__main__":
    pygame.init()
    #pygame.joystick.init() #scans system for any joysticks. Needs to be run for anything else with joysticks to work
    #joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    print(pygame.joystick.get_count()) 
    joystick = pygame.joystick.Joystick(0)
    num_of_buttons = joystick.get_numbuttons()
    print(joystick.get_name())
    
    # while True:
    #     for i in range(num_of_buttons):
    #         if joystick.get_button(i) == True:
    #             print(f'button {i} was pressed')

    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    while True:
        for event in pygame.event.get(): # User did something.
            if event.type == pygame.QUIT: # If user clicked close.
                done = True # Flag that we are done so we exit this loop.
            elif event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            elif event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")
            else:
                print('something happened')