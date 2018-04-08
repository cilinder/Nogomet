import sys, pygame
from math import *
from itertools import *

# define some color names for drawing
green = (0,255,0)
black = (0,0,0)
white = (255,255,255)
blue = (0, 0, 255)
red = (255, 0, 0)


# a <-> 0
# b <-> 1

class FootballField:

    turn = 1    # team 1 or team 2

    def __init__(self, V, E, L, team_1, team_2, ball):
        self.V = V
        self.E = E
        self.L = L
        self.team_1 = team_1
        self.team_2 = team_2
        self.ball = ball

    def same_vertex(self, v1, v2):

        loc1, table1 = v1
        loc2, table2 = v2

        return table1 == table2 and loc1[0] == loc2[0] and loc1[1] == loc2[1]


    def neighbors(self, v):

        return set(u for u in self.V if (u,v) in self.E or (v,u) in self.E)


    def all_empty_fields(self):

        return self.V - self.team_1 - self.team_2 - {self.ball}


    def possible_player_movements(self, player):

        return self.neighbors(player) - self.team_1 - self.team_2 - {self.ball}


    def possible_ball_moves(self):

        team = self.team_1

        empty_fields = self.all_empty_fields()
        ball_neighbors = self.neighbors(self.ball)
        adjacent_players = ball_neighbors & self.team_1
        adjacent_player_neighbors = set(chain.from_iterable(map(self.neighbors, adjacent_players)))

        return adjacent_player_neighbors & empty_fields & ball_neighbors


    def possible_kicks(self):

        empty_fields = self.all_empty_fields()
        ball_neighbors = self.neighbors(self.ball)
        players = ball_neighbors & self.team_1

        kicks = set()

        lines_with_ball = []
        indices = []
        for line in self.L:
            try:
                indices.append(line.index(self.ball))
                lines_with_ball.append(line)
            except ValueError:
                continue

        for player in players:
            for ind_ball, line in zip(indices, lines_with_ball):
                try:
                    ind_player = line.index(player)
                    direction = ind_ball - ind_player
                except ValueError:
                    continue


        for line in self.L:
            try:
                id_ball = line.index(self.ball)
                for player in players:
                    try:
                        id_player = line.index(player)
                        direction = id_ball - id_player
                        if direction == 1:
                            kick = line[id_ball+1:]
                        elif direction == -1:
                            kick = line[:id_ball]
                        kicks.update(kick)
                    except ValueError:
                        # player not in line
                        continue
            except ValueError:
                # ball not in line
                continue

        return kicks


    def is_possible_swap(self, player):

        # team represents the team whose turn it is, as only they can move then
        team = self.team_1
        return self.player in team and (player, self.ball) in self.E




def draw_horizontal(screen, color, P, r):
    for i in range(len(P)):
        for j in range(len(P[i]) - 1):

            x0, y0 = P[i][j]
            x1, y1 = P[i][j+1]
            pygame.draw.line(screen, color, (x0+r, y0), (x1-r,y1))


def draw_vertical(screen, color, P, r):
    for i in range(len(P) - 1):
        for j in range(len(P[i])):
            x0, y0 = P[i][j]
            x1, y1 = P[i+1][j]
            pygame.draw.line(screen, color, (x0, y0+r), (x1, y1-r))


def draw_diagonal(screen, color, A, B, r):

    for i in range(len(B)):
        for j in range(len(B[i])):

            x0,y0 = B[i][j]
            x1,y1 = A[i][j]
            x2,y2 = A[i][j+1]
            x3,y3 = A[i+1][j]
            x4,y4 = A[i+1][j+1]

            q = sqrt(2)/2 * r

            pygame.draw.line(screen, color, (x0 - q, y0 - q), (x1 + q, y1 + q))
            pygame.draw.line(screen, color, (x0 + q, y0 - q), (x2 - q, y2 + q))
            pygame.draw.line(screen, color, (x0 - q, y0 + q), (x3 + q, y3 - q))
            pygame.draw.line(screen, color, (x0 + q, y0 + q), (x4 - q, y4 - q))


def draw_positions(screen, A, B, r):

    white = (255,255,255)
    for row in A:
        for a in row:
            pygame.draw.circle(screen, white, a, r)

    for row in B:
        for b in row:
            pygame.draw.circle(screen, white, b, r)


def draw_players(screen, color, players, A, B, r):

    for player in players:
        loc, table = player
        i,j = loc

        if table == 0: # table is A
            pygame.draw.circle(screen, color, A[i][j], r)
        elif table == 1: # table is B
            pygame.draw.circle(screen, color, B[i][j], r)


def draw_ball(screen, color, ball, A, B, r):
    loc, table = ball
    i,j = loc

    if table == 0: # table is A
        pygame.draw.circle(screen, color, A[i][j], r)
    elif table == 1: # table is B
        pygame.draw.circle(screen, color, B[i][j], r)


def draw_field(screen, A, B, state, r = 12, dont_draw = []):


    team_1 = state.team_1 - set(dont_draw)
    team_2 = state.team_2 - set(dont_draw)

    draw_positions(screen, A, B, r)

    draw_horizontal(screen, black, A, r)
    draw_horizontal(screen, black, B, r)

    draw_vertical(screen, black, A, r)
    draw_vertical(screen, black, B, r)

    draw_diagonal(screen, black, A, B, r)

    if not state.ball in dont_draw:
        draw_ball(screen, blue, state.ball, A, B, r-3)

    draw_players(screen, black, team_1, A, B, r) # team 1 is black
    draw_players(screen, red, team_2, A, B, r)  # team 2 is red


def draw_goals(screen, color, goal_1, goal_2):

    pygame.draw.lines(screen, black, False, goal_1, 3) # draw the North goal
    pygame.draw.lines(screen, black, False, goal_2, 3) # draw the South goal


def create_edges(A,B):
    E = set()
    for i in range(len(A)):
        for j in range(len(A[i]) - 1):
            edge = (((i,j),0), ((i,j+1),0)) # a_ij -----> a_ij+1
            E.add(edge)

    for i in range(len(B)):
        for j in range(len(B[i]) - 1):
            edge = (((i,j),1), ((i,j+1),1)) # b_ij -----> b_ij+1
            E.add(edge)

    for i in range(len(A) - 1):
        for j in range(len(A[i])):
            edge = (((i,j),0), ((i+1,j),0))
            E.add(edge)

    for i in range(len(B) - 1):
        for j in range(len(B[i])):
            edge = (((i,j),1), ((i+1,j),1))
            E.add(edge)

    for i in range(len(B)):
        for j in range(len(B[i])):

            edge1 = ( ((i,j),1), ((i,j),0) )
            edge2 = ( ((i,j),1), ((i,j+1),0) )
            edge3 = ( ((i,j),1), ((i+1,j),0) )
            edge4 = ( ((i,j),1), ((i+1,j+1),0) )

            E.add(edge1)
            E.add(edge2)
            E.add(edge3)
            E.add(edge4)

    return E

def create_lines(A,B):
    L = []

    for i in range(len(A)):     # for each row in A
        line = []
        for j in range(len(A[i])):
            line.append( ((i,j),0) )
        if len(line) > 1:
            L.append(line)
    for i in range(len(B)):     # for each row in A
        line = []
        for j in range(len(B[i])):
            line.append( ((i,j),1) )
        if len(line) > 1:
            L.append(line)

    for i in range(len(A[0])):
        line = []
        for j in range(len(A)):
            line.append( ((j,i),0) )
        if len(line) > 1:
            L.append(line)

    for i in range(len(B[0])):
        line = []
        for j in range(len(B)):
            line.append( ((j,i),1) )
        if len(line) > 1:
            L.append(line)

    m = len(A)-1
    n = len(A[0])-1

    for k in range(1, n+1):
        line1 = []
        line2 = []
        i = 0
        j = k
        while i < m and j > 0:
            v1 = ((i,j),0)
            v2 = ((i,j-1),1)
            v3 = ((i,n-j),0)
            v4 = ((i,n-j),1)
            line1.append(v1)
            line1.append(v2)
            line2.append(v3)
            line2.append(v4)
            i+=1
            j-=1
        line1.append( ((i,j),0) )
        line2.append( ((i,n-j),0) )
        L.append(line1)
        L.append(line2)


    for k in range(1,m):
        line1 = []
        line2 = []
        i = k
        j = n

        while i < m and j > 0:
            v1 = ((i,j),0)
            v2 = ((i,j-1),1)
            v3 = ((i,n-j),0)
            v4 = ((i,n-j),1)
            line1.append(v1)
            line1.append(v2)
            line2.append(v3)
            line2.append(v4)
            i+=1
            j-=1
        line1.append( ((i,j),0) )
        line2.append( ((i,n-j),0) )
        L.append(line1)
        L.append(line2)

    return L

def getClickedVertex(x0,y0,A,B,r=12):
    v = None
    for i in range(len(A)):
        for j in range(len(A[i])):
            x1, y1 = A[i][j]
            if sqrt((x0-x1)**2 + (y0-y1)**2) < r:
                v = ((i,j),0)
                break
    for i in range(len(B)):
        for j in range(len(B[i])):
            x1, y1 = B[i][j]
            if sqrt((x0-x1)**2 + (y0-y1)**2) < r:
                v = ((i,j),1)
                break
    return v


def getCoordinates(v, A, B):

    loc, table = v
    i,j = loc
    if table == 0:
        return A[i][j]
    else:
        return B[i][j]




def main():

    # Initialize the engine
    pygame.init()

    rows = 5
    cols = 4
    block_edge = 120

    width = cols * block_edge
    height = rows * block_edge

    size = width, height

    screen = pygame.display.set_mode(size)

    # Draw the goals
    goalWidth = 80
    goalDist = 10
    goalDepth = 16

    screen.fill(green)

    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

    x0 = int((width - goalWidth)/2.0)
    y0 = goalDist
    x1 = int((width + goalWidth)/2.0)
    goal_1 = [ (x0, y0+goalDepth), (x0, y0), (x1, y0), (x1, y0+goalDepth) ]
    goal_2 = [ (x0, height-y0-goalDepth), (x0, height-y0), (x1, height-y0), (x1, height-y0-goalDepth) ]


    a = block_edge
    player_radius = 12
    A = [] #  a matrix of A rows coordinates
    B = []
    V = set() # vertices

    for j in range(rows-1):
        A_j = []
        B_j = []
        for i in range(cols):
            point = (int(round(a/2 + i * a)), a + j * a)
            A_j.append(point)
            V.add(((j,i), 0))

        A.append(A_j)
        if j == rows-2:
            break
        for i in range(1, cols):
            point = ( i * a, j * a + int(round(a + a/2)))
            B_j.append(point)
            V.add(((j,i-1), 1))
        B.append(B_j)

    E = create_edges(A,B)

    L = create_lines(A,B)

    team_1 = { ((0,0),1), ((0,1),1) }
    team_2 = { ((1,2),0) }
    ball = ((1,1),0)

    state = FootballField(V, E, L, team_1, team_2, ball)


    # The main execution loop
    running = True
    v = None
    while running:
        screen.fill(green)
        draw_field(screen, A, B, state, 12, [v])    # draw the field without the vertex v
        draw_goals(screen, black, goal_1, goal_2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x0,y0 = pygame.mouse.get_pos()
                v = getClickedVertex(x0,y0,A,B)

            elif event.type == pygame.MOUSEMOTION:
                if v == None:
                    continue
                # save the current mouse position
                x0,y0 = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                if v == None:
                    continue
                new_pos = None

                # we are moving the ball
                if state.same_vertex(v, state.ball):
                    moves = state.possible_ball_moves()
                    kicks = state.possible_kicks()
                    # test if the location of the mouse release of is inside a circle that represents a legal move (dribble/kick)
                    for move in moves:
                        x,y = getCoordinates(move, A,B)
                        if sqrt((x-x0)**2+(y-y0)**2) < player_radius:
                            new_pos = move
                            break
                    for kick in kicks:
                        x,y = getCoordinates(kick, A,B)
                        if sqrt((x-x0)**2+(y-y0)**2) < player_radius:
                            new_pos = kick
                            break
                # we are moving a player
                else:
                    moves = state.possible_player_movements(v)
                    for move in moves:
                        x,y = getCoordinates(move, A,B)
                        if sqrt((x-x0)**2+(y-y0)**2) < player_radius:
                            new_pos = move
                            break
                # this means the release point does not represent a legal move
                if new_pos == None:
                    v = None
                    continue
                # we are moving a player from team 1 (will have to change this so we can only move a player on the team whose turn it is)
                if v in state.team_1:
                    state.team_1.remove(v)
                    state.team_1.add(new_pos)
                elif v in state.team_2:
                    state.team_2.remove(v)
                    state.team_2.add(new_pos)
                # we are moving the ball
                elif state.same_vertex(state.ball, v):
                    state.ball = new_pos

                v = None

        # draw the thing we are moving, whether be it a player or the ball
        if not v == None and v in state.team_1:
            pygame.draw.circle(screen, black, (x0,y0), 12)
        elif not v == None and v in state.team_2:
            pygame.draw.circle(screen, red, (x0,y0), 12)
        elif not v == None and state.same_vertex(v, state.ball):
            pygame.draw.circle(screen, blue, (x0,y0), 9)


        pygame.display.flip()
    pygame.image.save(screen, "igrisce.bmp")


if __name__ == "__main__":

    main()

