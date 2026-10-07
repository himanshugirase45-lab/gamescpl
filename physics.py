import pymunk

def create_bird(space, x, y, bird_type):
    mass = 5
    radius = 15
    if bird_type == "heavy":
        mass = 15
        radius = 18
    elif bird_type == "speed":
        mass = 3
        radius = 12
        
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.5
    shape.friction = 0.5
    shape.collision_type = 1 # bird
    space.add(body, shape)
    return body, shape

def create_block(space, x, y, width, height, material):
    mass = 10
    if material == "wood": mass = 5
    elif material == "glass": mass = 2
    elif material == "stone": mass = 20
        
    moment = pymunk.moment_for_box(mass, (width, height))
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.elasticity = 0.3
    shape.friction = 0.7
    shape.collision_type = 2 # block
    space.add(body, shape)
    return body, shape

def create_enemy(space, x, y, radius):
    mass = 3
    moment = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, moment)
    body.position = (x, y)
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.4
    shape.friction = 0.6
    shape.collision_type = 3 # enemy
    space.add(body, shape)
    return body, shape

def create_ground(space, width, height):
    # Static body for the ground
    body = space.static_body
    shape = pymunk.Segment(body, (0, height - 100), (width, height - 100), 10)
    shape.elasticity = 0.4
    shape.friction = 1.0
    shape.collision_type = 4 # ground
    space.add(shape)
    
    # Left and right walls just in case
    wall_left = pymunk.Segment(body, (-100, -1000), (-100, height), 10)
    wall_left.friction = 1.0
    wall_right = pymunk.Segment(body, (width+1000, -1000), (width+1000, height), 10)
    wall_right.friction = 1.0
    space.add(wall_left, wall_right)
    return shape
