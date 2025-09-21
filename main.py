# import critical modules - random for board generation, copy for being able to restart, pygame for framework
import copy
import random
import pygame

# initialize pygame
pygame.init()

# initialize game variables
WIDTH = 1400  # Increased from 1000
HEIGHT = 700  # Increased from 550
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Water Sort PyGame')
font = pygame.font.Font('freesansbold.ttf', 24)
fps = 60
timer = pygame.time.Clock()
color_choices = ['red', 'orange', 'dark blue', 'dark green', 'pink', 'purple', 'dark gray',
                 'light green', 'yellow', 'white']
tube_colors = []
initial_colors = []
#always start with two empty
tubes = 5
new_game = True
selected = False
tube_rects = []
select_rect = 100
win = False
pop_push_mode = None  # None, 'pop', 'push', or 'queue'
pop_tube_index = None
push_tube_index = None
pop_button_rect = None
push_button_rect = None
queue_blocks = []  # stores color indices for queue
queue_selected = False
queue_mode = None  # None, 'queue', or 'dequeue'
queue_button_rect = None
dequeue_button_rect = None
queue_list = [[], []]  # Two queues, each can hold up to 4 blocks
queue_rects = []
selected_queue_index = None
dequeued_queue_index = None
dequeue_destination_type = None  # 'tube' or 'queue'
dequeue_destination_index = None

# select a number of tubes and pick random colors upon new game setup
def generate_start():
    tubes_number = 5
    tubes_colors = []
    available_colors = []
    for i in range(tubes_number):
        tubes_colors.append([])
        if i < tubes_number - 2:
            for j in range(4):
                available_colors.append(i)
    for i in range(tubes_number - 2):
        for j in range(4):
            color = random.choice(available_colors)
            tubes_colors[i].append(color)
            available_colors.remove(color)
    return tubes_number, tubes_colors


# draw all tubes and colors on screen, as well as indicating what tube was selected
def draw_tubes(tubes_num, tube_cols):
    global pop_button_rect, push_button_rect
    tube_boxes = []
    pop_button_rect = None
    push_button_rect = None
    if tubes_num % 2 == 0:
        tubes_per_row = tubes_num // 2
        offset = False
    else:
        tubes_per_row = tubes_num // 2 + 1
        offset = True
    spacing = WIDTH / tubes_per_row
    for i in range(tubes_per_row):
        for j in range(len(tube_cols[i])):
            pygame.draw.rect(screen, color_choices[tube_cols[i][j]], [5 + spacing * i, 200 - (50 * j), 65, 50], 0, 3)
        # Draw tube as a rectangle with no top border (open top)
        # Instead of: pygame.draw.rect(screen, 'blue', [x, y, w, h], 5, 5)
        # Draw left, right, and bottom borders only
        tube_x = 5 + spacing * i
        tube_y = 50
        tube_w = 65
        tube_h = 200
        # Left border
        pygame.draw.line(screen, 'blue', (tube_x, tube_y), (tube_x, tube_y + tube_h), 5)
        # Right border
        pygame.draw.line(screen, 'blue', (tube_x + tube_w, tube_y), (tube_x + tube_w, tube_y + tube_h), 5)
        # Bottom border
        pygame.draw.line(screen, 'blue', (tube_x, tube_y + tube_h), (tube_x + tube_w, tube_y + tube_h), 5)
        # Highlight selected tube
        if select_rect == i:
            pygame.draw.rect(screen, 'green', [tube_x, tube_y, tube_w, tube_h], 3, 5)
        # Draw Pop button if a tube is selected and not yet popped
        if selected and pop_push_mode is None and select_rect == i:
            pop_button_rect = pygame.draw.rect(screen, 'gray', [5 + spacing * i + 80, 100, 80, 40])
            pop_text = font.render('Pop', True, 'black')
            screen.blit(pop_text, (5 + spacing * i + 100, 110))
        # Draw Push button if in push mode and this is the destination tube
        if pop_push_mode == 'push' and push_tube_index == i:
            push_button_rect = pygame.draw.rect(screen, 'gray', [5 + spacing * i + 80, 160, 80, 40])
            push_text = font.render('Push', True, 'black')
            screen.blit(push_text, (5 + spacing * i + 95, 170))
        # Draw Push button if in dequeue_push mode and this is the destination tube
        if pop_push_mode == 'dequeue_push' and dequeue_destination_type == 'tube' and dequeue_destination_index == i:
            push_button_rect = pygame.draw.rect(screen, 'gray', [tube_x + 80, 160, 80, 40])
            push_text = font.render('Push', True, 'black')
            screen.blit(push_text, (tube_x + 95, 170))
        box = pygame.Rect(tube_x, tube_y, tube_w, tube_h)  # <-- ADD THIS LINE
        tube_boxes.append(box)
    if offset:
        for i in range(tubes_per_row - 1):
            for j in range(len(tube_cols[i + tubes_per_row])):
                pygame.draw.rect(screen, color_choices[tube_cols[i + tubes_per_row][j]],
                                 [(spacing * 0.5) + 5 + spacing * i, 450 - (50 * j), 65, 50], 0, 3)
            # Draw tube as a rectangle with no top border (open top)
            tube_x = (spacing * 0.5) + 5 + spacing * i
            tube_y = 300
            tube_w = 65
            tube_h = 200
            # Left border
            pygame.draw.line(screen, 'blue', (tube_x, tube_y), (tube_x, tube_y + tube_h), 5)
            # Right border
            pygame.draw.line(screen, 'blue', (tube_x + tube_w, tube_y), (tube_x + tube_w, tube_y + tube_h), 5)
            # Bottom border
            pygame.draw.line(screen, 'blue', (tube_x, tube_y + tube_h), (tube_x + tube_w, tube_y + tube_h), 5)
            # Highlight selected tube
            if select_rect == i + tubes_per_row:
                pygame.draw.rect(screen, 'green', [tube_x, tube_y, tube_w, tube_h], 3, 5)
            # Draw Pop button if a tube is selected and not yet popped
            if selected and pop_push_mode is None and select_rect == i + tubes_per_row:
                pop_button_rect = pygame.draw.rect(screen, 'gray', [tube_x + 80, 100, 80, 40])
                pop_text = font.render('Pop', True, 'black')
                screen.blit(pop_text, (tube_x + 100, 110))
            # Draw Push button if in push mode and this is the destination tube
            if pop_push_mode == 'push' and push_tube_index == i + tubes_per_row:
                push_button_rect = pygame.draw.rect(screen, 'gray', [tube_x + 80, 160, 80, 40])
                push_text = font.render('Push', True, 'black')
                screen.blit(push_text, (tube_x + 95, 170))
            # Draw Push button if in dequeue_push mode and this is the destination tube
            if pop_push_mode == 'dequeue_push' and dequeue_destination_type == 'tube' and dequeue_destination_index == i + tubes_per_row:
                push_button_rect = pygame.draw.rect(screen, 'gray', [tube_x + 80, 160, 80, 40])
                push_text = font.render('Push', True, 'black')
                screen.blit(push_text, (tube_x + 95, 170))
            box = pygame.Rect(tube_x, tube_y, tube_w, tube_h)
            tube_boxes.append(box)
    else:
        for i in range(tubes_per_row):
            for j in range(len(tube_cols[i + tubes_per_row])):
                pygame.draw.rect(screen, color_choices[tube_cols[i + tubes_per_row][j]], [5 + spacing * i,
                                                                                          450 - (50 * j), 65, 50], 0, 3)
            # Draw tube as a rectangle with no top border (open top)
            tube_x = 5 + spacing * i
            tube_y = 300
            tube_w = 65
            tube_h = 200
            # Left border
            pygame.draw.line(screen, 'blue', (tube_x, tube_y), (tube_x, tube_y + tube_h), 5)
            # Right border
            pygame.draw.line(screen, 'blue', (tube_x + tube_w, tube_y), (tube_x + tube_w, tube_y + tube_h), 5)
            # Bottom border
            pygame.draw.line(screen, 'blue', (tube_x, tube_y + tube_h), (tube_x + tube_w, tube_y + tube_h), 5)
            # Highlight selected tube
            if select_rect == i + tubes_per_row:
                pygame.draw.rect(screen, 'green', [tube_x, tube_y, tube_w, tube_h], 3, 5)
            # Draw Pop button if a tube is selected and not yet popped
            if selected and pop_push_mode is None and select_rect == i + tubes_per_row:
                pop_button_rect = pygame.draw.rect(screen, 'gray', [tube_x + 80, 100, 80, 40])
                pop_text = font.render('Pop', True, 'black')
                screen.blit(pop_text, (tube_x + 100, 110))
            # Draw Push button if in push mode and this is the destination tube
            if pop_push_mode == 'push' and push_tube_index == i + tubes_per_row:
                push_button_rect = pygame.draw.rect(screen, 'gray', [tube_x + 80, 160, 80, 40])
                push_text = font.render('Push', True, 'black')
                screen.blit(push_text, (tube_x + 95, 170))
            # Draw Push button if in dequeue_push mode and this is the destination tube
            if pop_push_mode == 'dequeue_push' and dequeue_destination_type == 'tube' and dequeue_destination_index == i + tubes_per_row:
                push_button_rect = pygame.draw.rect(screen, 'gray', [tube_x + 80, 160, 80, 40])
                push_text = font.render('Push', True, 'black')
                screen.blit(push_text, (tube_x + 95, 170))
            box = pygame.Rect(tube_x, tube_y, tube_w, tube_h)
            tube_boxes.append(box)
    return tube_boxes


# determine the top color of the selected tube and destination tube,
# as well as how long a chain of that color to move
def calc_move(colors, selected_rect, destination):
    color_on_top = 100
    length = 1
    color_to_move = 100
    if len(colors[selected_rect]) > 0:
        color_to_move = colors[selected_rect][-1]
    if 4 > len(colors[destination]):
        if len(colors[destination]) == 0:
            color_on_top = color_to_move
        else:
            color_on_top = colors[destination][-1]
    if color_on_top == color_to_move:
        for i in range(length):
            if len(colors[destination]) < 4:
                if len(colors[selected_rect]) > 0:
                    colors[destination].append(color_on_top)
                    colors[selected_rect].pop(-1)
    return colors


# check if every tube with colors is 4 long and all the same color for win condition
def check_victory(colors):
    won = True
    for i in range(len(colors)):
        if len(colors[i]) > 0:
            if len(colors[i]) != 4:
                won = False
            else:
                main_color = colors[i][-1]
                for j in range(len(colors[i])):
                    if colors[i][j] != main_color:
                        won = False
    return won


# draw queue blocks and buttons for enqueue/dequeue
def draw_queues(queue_list):
    global queue_rects, queue_button_rect, dequeue_button_rect
    queue_rects = []
    queue_w = 260  # 4 blocks * 65px
    queue_h = 65
    block_w = 65
    y = 600
    x_spacing = 400
    queue_button_rect = None
    dequeue_button_rect = None
    for idx in range(2):
        x = 300 + idx * x_spacing
        pygame.draw.line(screen, 'black', (x, y), (x + queue_w, y), 5)
        pygame.draw.line(screen, 'black', (x, y + queue_h), (x + queue_w, y + queue_h), 5)
        for i, color_idx in enumerate(queue_list[idx]):
            pygame.draw.rect(screen, color_choices[color_idx], [x + i * block_w, y, block_w, queue_h], 0, 3)
        # Highlight logic for all queue modes
        highlight = (
            (queue_selected and selected_queue_index == idx and pop_push_mode is None) or
            (pop_push_mode == 'queue' and selected_queue_index == idx) or
            (pop_push_mode == 'dequeue_queue' and dequeue_destination_type == 'queue' and dequeue_destination_index == idx)
        )
        if highlight:
            pygame.draw.rect(screen, 'green', [x, y, queue_w, queue_h], 3, 5)
        # Show Dequeue button if a queue is selected and not in dequeue mode
        if queue_selected and selected_queue_index == idx and pop_push_mode is None:
            dequeue_button_rect = pygame.draw.rect(screen, 'gray', [x + queue_w + 20, y, 80, 40])
            dequeue_text = font.render('Dequeue', True, 'black')
            screen.blit(dequeue_text, (x + queue_w + 35, y + 10))
        # Show Queue button if in dequeue_queue mode or pop->queue mode
        if ((pop_push_mode == 'dequeue_queue' and dequeue_destination_type == 'queue' and dequeue_destination_index == idx) or
            (pop_push_mode == 'queue' and selected_queue_index == idx)):
            queue_button_rect = pygame.draw.rect(screen, 'gray', [x + queue_w + 20, y, 80, 40])
            queue_text = font.render('Queue', True, 'black')
            screen.blit(queue_text, (x + queue_w + 35, y + 10))
        queue_rects.append(pygame.Rect(x, y, queue_w, queue_h))


# main game loop
run = True
while run:
    screen.fill('light blue')
    timer.tick(fps)
    # generate game board on new game, make a copy of the colors in case of restart
    if new_game:
        tubes, tube_colors = generate_start()
        initial_colors = copy.deepcopy(tube_colors)
        new_game = False
    # draw tubes every cycle
    else:
        tube_rects = draw_tubes(tubes, tube_colors)
        draw_queues(queue_list)
    # check for victory every cycle
    win = check_victory(tube_colors)
    # event handling - Quit button exits, clicks select tubes, enter and space for restart and new board
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                tube_colors = copy.deepcopy(initial_colors)
            elif event.key == pygame.K_RETURN:
                new_game = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Select tube or queue
            if not selected and not queue_selected:
                for item in range(len(tube_rects)):
                    if tube_rects[item].collidepoint(mouse_pos):
                        selected = True
                        select_rect = item
                        pop_push_mode = None
                        pop_tube_index = None
                        push_tube_index = None
                for q_idx, q_rect in enumerate(queue_rects):
                    if q_rect.collidepoint(mouse_pos):
                        queue_selected = True
                        selected_queue_index = q_idx
                        queue_button_rect = None
                        dequeue_button_rect = None
            # Stack logic: Pop selected
            elif selected and not queue_selected and pop_push_mode is None:
                if pop_button_rect and pop_button_rect.collidepoint(mouse_pos):
                    pop_push_mode = 'pop'
                    pop_tube_index = select_rect
                else:
                    selected = False
                    select_rect = 100
            # After pop, allow selecting either a tube (for push) or a queue (for queue)
            elif pop_push_mode == 'pop':
                for item in range(len(tube_rects)):
                    if tube_rects[item].collidepoint(mouse_pos) and item != pop_tube_index:
                        push_tube_index = item
                        select_rect = item
                        pop_push_mode = 'push'
                        break
                for q_idx, q_rect in enumerate(queue_rects):
                    if q_rect.collidepoint(mouse_pos):
                        queue_selected = True
                        selected_queue_index = q_idx
                        pop_push_mode = 'queue'
                        break
            # Show Queue button and handle queueing after pop
            elif pop_push_mode == 'queue' and queue_selected:
                if queue_button_rect and queue_button_rect.collidepoint(mouse_pos):
                    if len(tube_colors[pop_tube_index]) > 0 and len(queue_list[selected_queue_index]) < 4:
                        block = tube_colors[pop_tube_index].pop(-1)
                        queue_list[selected_queue_index].append(block)
                    selected = False
                    select_rect = 100
                    queue_selected = False
                    selected_queue_index = None
                    pop_push_mode = None
                    pop_tube_index = None
                else:
                    selected = False
                    select_rect = 100
                    queue_selected = False
                    selected_queue_index = None
                    pop_push_mode = None
                    pop_tube_index = None
            # Push mode, waiting for push button click after pop
            elif pop_push_mode == 'push':
                if push_button_rect and push_button_rect.collidepoint(mouse_pos):
                    if pop_tube_index is not None and push_tube_index is not None:
                        tube_colors = calc_move(tube_colors, pop_tube_index, push_tube_index)
                    selected = False
                    select_rect = 100
                    pop_push_mode = None
                    pop_tube_index = None
                    push_tube_index = None
                else:
                    selected = False
                    select_rect = 100
                    pop_push_mode = None
                    pop_tube_index = None
                    push_tube_index = None
            # Queue logic: only if both a queue and tube are selected
            elif queue_selected and pop_push_mode is None:
                if dequeue_button_rect and dequeue_button_rect.collidepoint(mouse_pos):
                    if queue_list[selected_queue_index]:
                        pop_push_mode = 'dequeue'
                        dequeued_queue_index = selected_queue_index
                        # Keep selected_queue_index for highlighting destination
                        queue_selected = False
                        # Do NOT set selected_queue_index = None here!
                else:
                    queue_selected = False
                    selected_queue_index = None
            # After dequeue, allow selecting either a tube (for push) or another queue (for queue)
            elif pop_push_mode == 'dequeue':
                # Select tube for push
                tube_clicked = False
                for item in range(len(tube_rects)):
                    if tube_rects[item].collidepoint(mouse_pos):
                        dequeue_destination_type = 'tube'
                        dequeue_destination_index = item
                        select_rect = item
                        pop_push_mode = 'dequeue_push'
                        queue_selected = False
                        selected_queue_index = None
                        tube_clicked = True
                        break
                # Only check queues if no tube was clicked
                if not tube_clicked:
                    for q_idx, q_rect in enumerate(queue_rects):
                        if q_rect.collidepoint(mouse_pos) and q_idx != dequeued_queue_index:
                            dequeue_destination_type = 'queue'
                            dequeue_destination_index = q_idx
                            queue_selected = True
                            selected_queue_index = q_idx
                            pop_push_mode = 'dequeue_queue'
                            break
            # Handle push after dequeue
            elif pop_push_mode == 'dequeue_push':
                if push_button_rect and push_button_rect.collidepoint(mouse_pos):
                    # Move dequeued block to selected tube
                    if queue_list[dequeued_queue_index] and len(tube_colors[dequeue_destination_index]) < 4:
                        block = queue_list[dequeued_queue_index].pop(0)
                        tube_colors[dequeue_destination_index].append(block)
                    # Reset selection
                    selected = False
                    select_rect = 100
                    queue_selected = False
                    selected_queue_index = None
                    pop_push_mode = None
                    dequeued_queue_index = None
                    dequeue_destination_type = None
                    dequeue_destination_index = None
                else:
                    selected = False
                    select_rect = 100
                    queue_selected = False
                    selected_queue_index = None
                    pop_push_mode = None
                    dequeued_queue_index = None
                    dequeue_destination_type = None
                    dequeue_destination_index = None
            # Handle queue after dequeue
            elif pop_push_mode == 'dequeue_queue':
                if queue_button_rect and queue_button_rect.collidepoint(mouse_pos):
                    # Move dequeued block to selected queue
                    if queue_list[dequeued_queue_index] and len(queue_list[dequeue_destination_index]) < 4:
                        block = queue_list[dequeued_queue_index].pop(0)
                        queue_list[dequeue_destination_index].append(block)
                    selected = False
                    select_rect = 100
                    queue_selected = False
                    selected_queue_index = None
                    pop_push_mode = None
                    dequeued_queue_index = None
                    dequeue_destination_type = None
                    dequeue_destination_index = None
                else:
                    selected = False
                    select_rect = 100
                    queue_selected = False
                    selected_queue_index = None
                    pop_push_mode = None
                    dequeued_queue_index = None
                    dequeue_destination_type = None
                    dequeue_destination_index = None
            # If only queue is selected, allow deselect
            elif queue_selected and not selected:
                queue_selected = False
                selected_queue_index = None
            # If only tube is selected, allow deselect
            elif selected and not queue_selected:
                selected = False
                select_rect = 100

    # draw 'victory' text when winning in middle, always show restart and new board text at top
    if win:
        victory_text = font.render('You Won! Press Enter for a new board!', True, 'white')
        screen.blit(victory_text, (30, 265))
    #restart_text = font.render('Stuck? Space-Restart, Enter-New Board!', True, 'white')
    #screen.blit(restart_text, (10, 10))

    # display all drawn items on screen, exit pygame if run == False
    pygame.display.flip()
pygame.quit()