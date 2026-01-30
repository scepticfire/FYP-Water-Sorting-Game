#import critical modules - random for board generation, copy for being able to restart, pygame for framework
import copy
import random
import pygame

#initialize pygame
pygame.init()

#initialize game variables
WIDTH = 1600 
HEIGHT = 900 
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Water Sort PyGame')
font = pygame.font.Font('freesansbold.ttf', 24)
label_font = pygame.font.Font('freesansbold.ttf', 20) #Used for LIFO and FIFO labels
fps = 60
timer = pygame.time.Clock()
color_choices = ['red', 'orange', 'purple', 'dark green']
tube_colors = []
initial_colors = []
#always start with two empty
tubes = 3
new_game = True
selected = False
tube_rects = []
select_rect = 100
win = False
pop_push_mode = None  #None, 'pop', 'push', or 'enqueue'
pop_tube_index = None
push_tube_index = None
pop_button_rect = None
push_button_rect = None
queue_blocks = []  #stores color indices for queue
queue_selected = False
queue_mode = None  #None, 'enqueue', or 'dequeue'
queue_button_rect = None
dequeue_button_rect = None
queue_list = [[], [], []]  #3 queues, each can hold up to 4 blocks
queue_rects = []
selected_queue_index = None
dequeued_queue_index = None
dequeue_destination_type = None  # 'tube' or 'enqueue'
dequeue_destination_index = None
victory_button_rect = None

# select a number of tubes and pick random colors upon new game setup
def generate_start():
    tubes_number = 3
    tubes_colors = [[] for _ in range(tubes_number)]

    # 4 colors × 4 blocks = 16 total
    color_pool = []
    for color in range(len(color_choices)):
        color_pool.extend([color] * 4)

    random.shuffle(color_pool)

    # Fill ONLY first 2 stacks
    for i in range(2):
        for _ in range(4):
            tubes_colors[i].append(color_pool.pop())

    # Leave 3rd stack empty
    tubes_colors[2] = []

    # Fill ONLY first 2 queues
    for q in range(2):
        queue_list[q] = []
        for _ in range(4):
            queue_list[q].append(color_pool.pop())

    # Leave 3rd queue empty
    queue_list[2] = []

    return tubes_number, tubes_colors


def draw_tubes(tubes_num, tube_cols):
    global pop_button_rect, push_button_rect

    tube_boxes = []
    pop_button_rect = None
    push_button_rect = None

    tube_w = 65
    tube_h = 200
    spacing = 200

    layout_width = tubes_num * tube_w + (tubes_num - 1) * spacing
    left_margin = (WIDTH - layout_width) / 2
    tube_y = 80

    for i in range(tubes_num):
        tube_x = left_margin + i * (tube_w + spacing)

        # draw blocks
        for j in range(len(tube_cols[i])):
            pygame.draw.rect(
                screen,
                color_choices[tube_cols[i][j]],
                [tube_x, tube_y + tube_h - 50 * (j + 1), tube_w, 50],
                0, 3
            )

        # tube outline
        pygame.draw.rect(screen, 'blue', [tube_x, tube_y, tube_w, tube_h], 5)

        # label
        lifo_text = label_font.render('Stack (LIFO)', True, 'black')
        screen.blit(lifo_text, (tube_x + tube_w / 2 - 45, tube_y + tube_h + 10))

        # highlight selected
        if select_rect == i:
            pygame.draw.rect(screen, 'green', [tube_x, tube_y, tube_w, tube_h], 3, 5)

        # ===============================
        # POP BUTTON (when stack selected)
        # ===============================
        if selected and select_rect == i and pop_push_mode is None:
            pop_button_rect = pygame.draw.rect(
                screen, 'gray',
                [tube_x - 10, tube_y + tube_h + 45, 85, 40]
            )
            pop_text = font.render('Pop', True, 'black')
            screen.blit(pop_text, (tube_x + 10, tube_y + tube_h + 52))

            # RED arrow (upwards)
            pygame.draw.line(
                screen, 'red',
                (tube_x + tube_w / 2, tube_y - 10),
                (tube_x + tube_w / 2, tube_y - 40),
                5
            )
            pygame.draw.polygon(
                screen, 'red',
                [
                    (tube_x + tube_w / 2, tube_y - 40),
                    (tube_x + tube_w / 2 - 8, tube_y - 28),
                    (tube_x + tube_w / 2 + 8, tube_y - 28)
                ]
            )

        # ===============================
        # PUSH BUTTON (after pop)
        # ===============================
        if pop_push_mode in ('push', 'dequeue_push') and select_rect == i:
            push_button_rect = pygame.draw.rect(
                screen, 'gray',
                [tube_x - 10, tube_y + tube_h + 45, 85, 40]
            )
            push_text = font.render('Push', True, 'black')
            screen.blit(push_text, (tube_x + 5, tube_y + tube_h + 52))

            # GREEN arrow (downwards)
            pygame.draw.line(
                screen, 'green',
                (tube_x + tube_w / 2, tube_y - 40),
                (tube_x + tube_w / 2, tube_y - 10),
                5
            )
            pygame.draw.polygon(
                screen, 'green',
                [
                    (tube_x + tube_w / 2, tube_y - 10),
                    (tube_x + tube_w / 2 - 8, tube_y - 22),
                    (tube_x + tube_w / 2 + 8, tube_y - 22)
                ]
            )

        tube_boxes.append(pygame.Rect(tube_x, tube_y, tube_w, tube_h))

    return tube_boxes

# draw queue blocks and buttons for enqueue/dequeue
def draw_queues(queue_list):
    global queue_rects, queue_button_rect, dequeue_button_rect
    queue_rects = []
    queue_w = 260
    queue_h = 65
    block_w = 65
    y = 500
    spacing = 180  # distance between the two queues
    layout_width = 3 * queue_w + 2 * spacing
    left_margin = (WIDTH - layout_width) / 2  # center horizontally

    queue_button_rect = None
    dequeue_button_rect = None

    for idx in range(3):
        x = left_margin + idx * (queue_w + spacing)
        pygame.draw.line(screen, 'black', (x, y), (x + queue_w, y), 5)
        pygame.draw.line(screen, 'black', (x, y + queue_h), (x + queue_w, y + queue_h), 5)

        #draw colored blocks
        for i, color_idx in enumerate(queue_list[idx]):
            pygame.draw.rect(screen, color_choices[color_idx], [x + i * block_w, y, block_w, queue_h], 0, 3)

        #highlight data structure when selected
        highlight = (
            (queue_selected and selected_queue_index == idx and pop_push_mode is None) or
            (pop_push_mode == 'enqueue' and selected_queue_index == idx) or
            (pop_push_mode == 'dequeue_queue' and dequeue_destination_type == 'enqueue' and dequeue_destination_index == idx) or
            (pop_push_mode == 'dequeue' and dequeued_queue_index == idx)
        )
        if highlight:
            pygame.draw.rect(screen, 'green', [x, y, queue_w, queue_h], 3, 5)

        #button creation and arrows
        if queue_selected and selected_queue_index == idx and pop_push_mode is None:
            dequeue_button_rect = pygame.draw.rect(screen, 'gray', [x + queue_w + 20, y, 130, 40])
            dequeue_text = font.render('Dequeue', True, 'black')
            screen.blit(dequeue_text, (x + queue_w + 35, y + 10))
                # RED dequeue arrow (pointing LEFT)
            arrow_y = y + queue_h / 2
            arrow_start = x - 10
            arrow_end = x - 70

            pygame.draw.line(
                screen, 'red',
                (arrow_start, arrow_y),
                (arrow_end, arrow_y),
                5
            )

            pygame.draw.polygon(
                screen,
                'red',
                [
                    (arrow_end, arrow_y),
                    (arrow_end + 12, arrow_y - 8),
                    (arrow_end + 12, arrow_y + 8)
                ]
            )

        if ((pop_push_mode == 'dequeue_queue' and dequeue_destination_type == 'enqueue' and dequeue_destination_index == idx)
            or (pop_push_mode == 'enqueue' and selected_queue_index == idx)):
            queue_button_rect = pygame.draw.rect(screen, 'gray', [x + queue_w + 20, y + 70, 130, 40])
            queue_text = font.render('Enqueue', True, 'black')
            screen.blit(queue_text, (x + queue_w + 35, y + 80))
            # GREEN enqueue arrow (pointing LEFT into queue)
            arrow_y = y + queue_h / 2
            arrow_start = x + queue_w + 70
            arrow_end = x + queue_w + 10

            pygame.draw.line(
                screen, 'green',
                (arrow_start, arrow_y),
                (arrow_end, arrow_y),
                5
            )

            pygame.draw.polygon(
                screen,
                'green',
                [
                    (arrow_end, arrow_y),
                    (arrow_end + 12, arrow_y - 8),
                    (arrow_end + 12, arrow_y + 8)
                ]
            )
            

        queue_rects.append(pygame.Rect(x, y, queue_w, queue_h))

        #label the word FIFO for queues
        label = label_font.render('Queue (FIFO)', True, 'black')
        screen.blit(label, (x + queue_w / 2 - 45, y + queue_h + 10))

# determine the top color of the selected tube and destination tube,
# as well as how long a chain of that color to move
def calc_move(colors, selected_rect, destination):
    if (
        selected_rect is not None
        and destination is not None
        and colors[selected_rect]
        and len(colors[destination]) < 4
    ):
        block = colors[selected_rect].pop(-1)
        colors[destination].append(block)
    return colors


#check if the queues/stacks holding the colour blocks are fully filled for the win condition
def check_victory(stacks, queues):
    def structure_complete(struct):
        if len(struct) == 0:
            return True
        if len(struct) != 4:
            return False
        first_color = struct[0]
        return all(block == first_color for block in struct)

    # Check all stacks
    for stack in stacks:
        if not structure_complete(stack):
            return False

    # Check all queues
    for queue in queues:
        if not structure_complete(queue):
            return False

    return True




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
    win = check_victory(tube_colors, queue_list)
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
            if win and victory_button_rect and victory_button_rect.collidepoint(mouse_pos):
                new_game = True
                win = False
                selected = False
                queue_selected = False
                pop_push_mode = None
                continue
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
            #Pop was selected
            elif selected and not queue_selected and pop_push_mode is None:
                if pop_button_rect and pop_button_rect.collidepoint(mouse_pos):
                    pop_push_mode = 'pop'
                    pop_tube_index = select_rect
                else:
                    selected = False
                    select_rect = 100
            #then allows selecting either a stack (for push) or a queue (for queue)
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
                        pop_push_mode = 'enqueue'
                        break
            #Shows enueue btn and handle queueing after pop
            elif pop_push_mode == 'enqueue' and queue_selected:
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
                        # Keep queue_selected and selected_queue_index for highlighting
                        # Do NOT set queue_selected = False or selected_queue_index = None here!
                else:
                    queue_selected = False
                    selected_queue_index = None
            # After dequeue, allow selecting either a tube (for push) or another queue (for queue)
            elif pop_push_mode == 'dequeue':
                tube_clicked = False
                for item in range(len(tube_rects)):
                    if tube_rects[item].collidepoint(mouse_pos):
                        dequeue_destination_type = 'tube'
                        dequeue_destination_index = item
                        select_rect = item
                        selected = True  # <-- ADD THIS LINE
                        push_tube_index = item  # <-- ADD THIS LINE
                        pop_push_mode = 'dequeue_push'
                        tube_clicked = True
                        break
                if not tube_clicked:
                    for q_idx, q_rect in enumerate(queue_rects):
                        if q_rect.collidepoint(mouse_pos) and q_idx != dequeued_queue_index:
                            dequeue_destination_type = 'enqueue'
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
        message = "You won! Click the button to start a new game"
        text_surface = font.render(message, True, 'black')

        # Position between stacks and queues
        center_y = (80 + 200 + 500) // 2  # midpoint between stacks & queues
        text_x = WIDTH // 2 - text_surface.get_width() // 2 - 80
        text_y = center_y

        screen.blit(text_surface, (text_x, text_y))

        # Draw button
        victory_button_rect = pygame.draw.rect(
            screen,
            'gray',
            [text_x + text_surface.get_width() + 20, text_y - 5, 120, 40],
            border_radius=6
        )

        button_text = font.render("New Game", True, 'black')
        screen.blit(
            button_text,
            (
                victory_button_rect.centerx - button_text.get_width() // 2,
                victory_button_rect.centery - button_text.get_height() // 2
            )
        )
    #restart_text = font.render('Stuck? Space-Restart, Enter-New Board!', True, 'white')
    #screen.blit(restart_text, (10, 10))

    # display all drawn items on screen, exit pygame if run == False
    pygame.display.flip()
pygame.quit()