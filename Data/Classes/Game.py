import pygame
import eztext
import string
import copy
class Game(): 
    def __init__(self): 
        self.game_window = pygame.display.set_mode((1280, 800))
        self.game_surface = pygame.Surface((self.game_window.get_size())).convert()
        self.game_surface.fill((255, 255, 255))
        self.game_window.blit(self.game_surface,  (0, 0))
        self.shape_group = pygame.sprite.Group()
        self.days_since_start = 0
        self.day = 0
        self.year = 1850
        self.season = ""
        
    def run_background(self): 
        keep_moving = True
        move_counter = 0
        while keep_moving: 
            if move_counter > 20: 
                keep_moving = False
            self.shape_group.clear(self.game_window,  self.game_surface)
            self.shape_group.update(self)
            self.shape_group.draw(self.game_window)
            pygame.display.flip()
            move_counter += 1
        pygame.display.flip()

    def calculations(self): 
        change_list = []
        self.day += 1
        self.days_since_start += 1
        print "-------------------------------"
        
        if self.day == 366: 
            self.year += 1
            self.day = 1
            
        if 1 <= self.day <= 80 or 356 <= self.day <= 365: 
            self.season = "Winter"
        elif 81 <= self.day <= 171: 
            self.season = "Spring"
        elif 172 <= self.day <= 262: 
            self.season = "Summer"
        elif 263 <= self.day <= 355: 
            self.season = "Autumn"

        for passenger in passenger_list: 
            total_hp_change = 0
            for affliction in passenger.afflictions:
                affliction.recovery_time -= 1
                if affliction.recovery_time == 0: 
                    passenger.afflictions.remove(affliction)
                    groupAfflictions.remove(affliction)
                    change_list.append(passenger.name +" has recovered from "+str(affliction.name))
                else:
                    total_hp_change += affliction.health_change
            if food_divisions[passenger.name] < 2: 
                total_hp_change -= 5* 2-food_divisions[passenger.name]
            elif food_divisions[passenger.name] > 2: 
                total_hp_change += 5*(food_divisions[passenger.name]-2)

            if total_hp_change != 0: 
                gainOrLoss = " lost "
                if total_hp_change > 0: 
                    gainOrLoss = " gained "
                passenger.health += total_hp_change
                if passenger.health < 0:  passenger.health = 0
                elif passenger.health > 100:  passenger.health = 100
                change_list.append(passenger.name +" has"+gainOrLoss+str(abs(total_hp_change))+" health for a total of "+str(passenger.health))
            
            if passenger.health <= 0: 
                passenger_list.remove(passenger)
                deceasedList.append(passenger)
                change_list.append(passenger.name+" has died.")
                if len(passenger_list) == 0: 
                    print"They're all dead,  Jim."
                break
            for affliction in afflictions_list: 
                modifier = 0
                if affliction in groupAfflictions and affliction not in passenger.afflictions: 
                    modifier = affliction.infectivity
                if affliction not in passenger.afflictions: 
                    randChance = round(random.uniform(0, 100), 2)
                    if randChance <= affliction.chance_to_infect + modifier: 
                        randDuration = random.randint(affliction.recovery_time[0],  affliction.recovery_time[1])
                        copyAffliction = copy.copy(affliction)
                        passenger.afflictions.append(copyAffliction)
                        for x in passenger.afflictions: 
                            if x.name == affliction.name:    
                                x.recovery_time = randDuration
                                change_list.append(str(passenger.name)+" has contracted "+str(affliction.name)+" for "+str(randDuration)+" days.")
                        groupAfflictions.append(affliction)
        print "Day : "+str(self.days_since_start)
        if len(change_list)==0:
            print"Nothing happened."
        else:
            for change in change_list:
                print change
        print "-------------------------------"

    def begin_play(self): 
        while(True): 
            clock.tick(60)
            for event in pygame.event.get(): 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: 
                        self.run_background()
                        self.calculations()

    def char_create(self): 
        text_entry = eztext.Input(maxlength=10,  color=(0, 0, 255),  prompt="")
        exit_button = pygame.image.load(resource_path+"Images\\exit.jpg")
        exit_button_rect = exit_button.get_rect()
        exit_button_rect.centerx = self.game_window.get_width() - exit_button.get_width()/2
        exit_button_rect.centery = exit_button.get_height()/2

        prompt_list = ["First Name", "Last Name", "Age", "Gender"]

        confirm_button = pygame.image.load(resource_path+"Images\\confirmbutton.jpg")
        confirm_button_rect = confirm_button.get_rect()
        confirm_button_rect.centerx = confirm_button.get_width()*1.5
        confirm_button_rect.centery = confirm_button.get_height()*1.5
        face_list = []
        for x in range(2): 
            entering_text = True
            pick_face = False
            text_prompt_counter = 0
            text_entry_responses = []
            text_entry = eztext.Input(maxlength=10,  color=(0, 0, 255),  prompt=prompt_list[text_prompt_counter]+":  ")

            while entering_text: 
                events = pygame.event.get()
                for event in events: 
                    if event.type == pygame.MOUSEMOTION: 
                        mouse_x, mouse_y = event.pos
                    if event.type == pygame.MOUSEBUTTONDOWN and exit_button_rect.collidepoint(mouse_x, mouse_y): 
                        pygame.quit()
                        quit()
                    if (event.type == pygame.MOUSEBUTTONDOWN and confirm_button_rect.collidepoint(mouse_x, mouse_y) or \
                       (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN)) and pick_face == False:
                        is_error = False

                        # First Name
                        if text_prompt_counter == 0:
                            if not all([x in string.letters for x in str(text_entry.value)]) and str(text_entry.value) != "":
                                is_error = True

                        # Last Name
                        elif text_prompt_counter == 1:
                            if not all([x in string.letters for x in str(text_entry.value)]) and str(text_entry.value) != "":
                                is_error = True

                        # Age
                        elif text_prompt_counter == 2:
                            if not all([x in string.digits for x in str(text_entry.value)]) and str(text_entry.value) != "":
                                is_error = True

                        # Gender
                        elif text_prompt_counter == 3:
                            if not all([x in string.letters for x in str(text_entry.value)]) and str(text_entry.value) != "":
                                is_error = True

                        if text_prompt_counter < 4 and is_error == False:
                            text_entry_responses.append(str(text_entry.value))
                            print text_entry_responses
                            if text_prompt_counter != 3:
                                text_prompt_counter += 1
                                text_entry = eztext.Input(maxlength=10,  color=(0, 0, 255),  prompt=prompt_list[text_prompt_counter]+":  ")
                                print str(text_prompt_counter)
                            else:
                                for path in picture_list:
                                    face_list.append(ShowFaces(file_path=path,x_pos=(picture_list.index(path)*100+50),y_pos=100))
                                for face in face_list:
                                    face.create()
                                pick_face = True

                        else:
                            print"Invalid Entry for "+prompt_list[text_prompt_counter]

                    if pick_face:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            for face in face_list:
                                if face.face_rect.collidepoint(mouse_x,mouse_y):
                                    print face.file_path
                                    for replace in face_list:
                                        if replace != face:
                                            replace.y_pos = 200
                                        else:
                                            replace.y_pos = 100
                                        replace.update()


                self.game_surface.fill((255, 255, 255))
                self.game_window.blit(self.game_surface, (0, 0))
                self.game_window.blit(exit_button,  (self.game_window.get_width()-exit_button.get_width(), 0))
                self.game_window.blit(confirm_button,  (100, 50))
                for face in face_list:
                    self.game_window.blit(face.image,(face.x_pos,face.y_pos))
                try:
                    text_entry.update(events)
                    text_entry.draw(self.game_window)
                except:
                    pass
                pygame.display.flip()
    
        for p in passenger_list: print p
        for passenger in passenger_list: 
            food_divisions[str(passenger.name)] = 2
        self.game_surface.fill((255, 255, 255))
        self.game_window.blit(self.game_surface, (0, 0))
        pygame.display.flip()
        self.begin_play()


    def title_screen(self): 
        play_button_col = (0, 0, 255)
        intitle_screen = True
        title = True
        while intitle_screen: 
            self.game_surface.fill((255, 255, 255))
            if title == True: 
                play_button = pygame.draw.rect(self.game_surface,  play_button_col,  (self.game_window.get_width()/2-100, self.game_window.get_height()/2-25, 200, 50))
                playFont = pygame.font.Font(None,  36)
                play_text= playFont.render("Play",  1,  (10,  10,  10))
                play_text_pos = play_text.get_rect()
                play_text_pos.centerx = self.game_window.get_rect().centerx
                play_text_pos.centery = self.game_window.get_rect().centery
                exit_button = pygame.image.load(resource_path+"Images\\exit.jpg")
                exit_button_rect = exit_button.get_rect()
                exit_button_rect.centerx = self.game_window.get_width() - exit_button.get_width()/2
                exit_button_rect.centery = exit_button.get_height()/2
            
            self.game_window.blit(self.game_surface, (0, 0))
            if title:  self.game_window.blit(play_text,  play_text_pos )
            self.game_window.blit(exit_button,  (self.game_window.get_width()-exit_button.get_width(), 0))
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    pygame.quit()
                if event.type == pygame.MOUSEMOTION: 
                    mouse_x, mouse_y = event.pos
                if event.type == pygame.MOUSEBUTTONDOWN: 
                    if title == True and play_button.collidepoint(mouse_x, mouse_y): 
                        play_button_col = (0, 0, 175)
                    if exit_button_rect.collidepoint(mouse_x, mouse_y): 
                        pygame.quit()
                        quit()
                if event.type == pygame.MOUSEBUTTONUP: 
                    play_button_col = (0, 0, 255)
                    if title == True and play_button.collidepoint(mouse_x, mouse_y): 
                        self.game_surface.fill((255, 255, 255))
                        self.game_window.blit(self.game_surface, (0, 0))
                        title = False
                        intitle_screen = False
            pygame.display.flip()
        self.char_create()
