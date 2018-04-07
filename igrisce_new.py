import sys, pygame
from math import *
from itertools import *

# define some color names for drawing
green = (0,255,0)
black = (0,0,0)
white = (255,255,255)
blue = (0, 0, 255)
red = (255, 0, 0)

# TODO: Convert graph implementation from list to set

# a <-> 0
# b <-> 1

class FootballField:

    turn = 1    # team 1 or team 2

    def __init__(self, V, E, team_1, team_2, ball):
        self.V = V
        self.E = E
        self.team_1 = team_1
        self.team_2 = team_2
        self.ball = ball
    
    def same_vertex(self, v1, v2):
    
        loc1, table1 = v1
        loc2, table2 = v2

        return table1 == table2 and loc1[0] == loc2[0] and loc1[1] == loc2[1]
     
     
    def neighbors(self, v):
        neighbors = []
        for v1, v2 in self.E:
            if self.same_vertex(v,v1):
                neighbors.append(v2)
            elif self.same_vertex(v,v2):
                neighbors.append(v1)
        return neighbors
        

    def all_empty_fields(self):
        
        F = [v for v in self.V if not v in self.team_1 and not v in self.team_2 and not self.same_vertex(v, self.ball)]
        return F
        
    def possible_player_movements(self, player):
        v0 = player
        moves = []
        for v1, v2 in self.E:
            if self.same_vertex(v0,v1):
                moves.append(v2)
            elif self.same_vertex(v0,v2):
                moves.append(v1)
        
        moves = [move for move in moves if move not in self.team_1 and move not in self.team_2 and not self.same_vertex(move, self.ball)]
        return moves
        

    def possible_ball_moves(self):

        moves = []
        empty_fields = self.all_empty_fields()
        
        ball_neighbors = []
        
        for v1, v2 in self.E:
            if self.same_vertex(self.ball, v1):
                ball_neighbors.append(v2)
            elif self.same_vertex(self.ball, v2):
                ball_neighbors.append(v1)
        
        # all the players that are standing next to the ball (i.e. can move it)
        players = [v for v in ball_neighbors if v in self.team_1]
        
        # all the empty fields adjacent to the ball
        empty_fields_ball = [v for v in ball_neighbors if not v in self.team_1 and not v in self.team_2]
        
        # the neighboring vertices of all the players next to the ball (i.e. where they can move it)
        player_neighbors = list(chain.from_iterable([(v for v in self.neighbors(p)) for p in players]))

        # player moves the ball around him
        for v in empty_fields_ball:
            for n in player_neighbors:
                if self.same_vertex(v, n):
                    moves.append(v)
                    break

        return moves
        
        
    def possible_kicks(self):

        empty_fields = self.all_empty_fields()
        ball_neighbors = self.neighbors(self.ball)
        team = self.team_1

        # all the players that are standing next to the ball (i.e. can move it)
        players = [v for v in ball_neighbors if v in team]
        # player kicks the ball forward
        kicks = []
        loc_ball, table_ball = self.ball
        for player in players:
            loc, table = player
            if table == table_ball:     # the ball is in the same table -> its either horizontal or vertical
                if loc[0] == loc_ball[0]:    # horizontal 
                    diff = loc[1] - loc_ball[1]
                    k = loc_ball[1] - diff
                    v = ((loc[0], k), table)
                    while v in empty_fields:
                        kicks.append(v)
                        k -= diff
                        v = ((loc[0], k), table)
                elif loc[1] == loc_ball[1]:     # vertical
                    diff = loc[0] - loc_ball[0]
                    k = loc_ball[0] - diff
                    v = ((k, loc[1]), table)
                    while v in empty_fields:
                        kicks.append(v)
                        k -= diff
                        v = ((k, loc[1]), table)
                        
            else:       # the ball is in a different table --> diagonal     
                print(player)
                print(self.ball)
                diff_row = loc[0] - loc_ball[0]
                diff_col = loc[1] - loc_ball[1]
                
                if table_ball == 1:     # the ball is in table B_j
                    k = loc_ball[0] - diff_row + 1
                    l = loc_ball[1] - diff_col + 1
                else:
                    k = loc_ball[0] - diff_row - 1
                    l = loc_ball[1] - diff_col - 1
                v = ((k,l), (table_ball+1) % 2)
                while v in empty_fields:
                    kicks.append(v)
                    #k = k - diff_row - (v[1]+1)%2
                    k = k - diff_row
                    #l = l - diff_col - (v[1]+1)%2
                    l = l - diff_col
                    v = ((k,l), (v[1]+1)%2)
                    
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

    
    team_1 = list(set(state.team_1)-set(dont_draw))
    team_2 = list(set(state.team_2)-set(dont_draw))
    
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
    
    """
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
        
    """
    
    m = len(A)-1
    n = len(A[0])-1
    
    for k in range(1, n+1):
        line = []
        j = 0
        i = k
        while j < min(k, m):
            v1 = ((j,i),0)
            v2 = ((j,i-1),1)
            line.append(v1)
            line.append(v2)
            j+=1
            i-=1
        line.append( ((min(k,m),i),0) )
        L.append(line)

        
    for k in range(1,m):
        line = []
        i = n
        j = k
        while i < k:
            v1 = ((i,j),0)
            v2 = ((i,j-1),1)
            line.append(v1)
            line.append(v2)
            i+=1
            j-=1
        line.append( ((max(k-1,),0) )
        L.append(line)
        
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

    rows = 6
    cols = 2
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
    
    print("lines: ")
    for line in L:
        print(line)

       
        
    team_1 = [   ]
    team_2 = [  ]
    ball = ((0,0),0)
    
    state = FootballField(V, E, team_1, team_2, ball)
    
    
    screen.fill(green)
    draw_field(screen, A, B, state, 12)    # draw the field without the vertex v
    draw_goals(screen, black, goal_1, goal_2)
    pygame.display.flip()
    pygame.image.save(screen, "igrisce.bmp")

    return 
    
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
                x0,y0 = pygame.mouse.get_pos()  
            elif event.type == pygame.MOUSEBUTTONUP:
                if v == None:
                    continue
                new_pos = None
                
                if state.same_vertex(v, state.ball):
                    moves = state.possible_ball_moves()
                    kicks = state.possible_kicks()
                    print(kicks)
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
                else:
                    moves = state.possible_player_movements(v)
                    for move in moves:
                        x,y = getCoordinates(move, A,B)
                        if sqrt((x-x0)**2+(y-y0)**2) < player_radius:
                            new_pos = move
                            break  
                if new_pos == None:
                    v = None
                    continue
                if v in state.team_1:
                    state.team_1 = list((set(state.team_1)-set([v])) | set([new_pos]) )
                elif v in state.team_2:
                    state.team_2 = list((set(state.team_2)-set([v])) | set([new_pos]) )
                elif state.same_vertex(state.ball, v):
                    state.ball = new_pos
                v = None
                break

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

